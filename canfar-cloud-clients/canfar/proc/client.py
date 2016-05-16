# -*- coding: utf-8 -*-
# ************************************************************************
# *******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# **************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
# *
# *  (c) 2015.                            (c) 2015.
# *  Government of Canada                 Gouvernement du Canada
# *  National Research Council            Conseil national de recherches
# *  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
# *  All rights reserved                  Tous droits réservés
# *
# *  NRC disclaims any warranties,        Le CNRC dénie toute garantie
# *  expressed, implied, or               énoncée, implicite ou légale,
# *  statutory, of any kind with          de quelque nature que ce
# *  respect to the software,             soit, concernant le logiciel,
# *  including without limitation         y compris sans restriction
# *  any warranty of merchantability      toute garantie de valeur
# *  or fitness for a particular          marchande ou de pertinence
# *  purpose. NRC shall not be            pour un usage particulier.
# *  liable in any event for any          Le CNRC ne pourra en aucun cas
# *  damages, whether direct or           être tenu responsable de tout
# *  indirect, special or general,        dommage, direct ou indirect,
# *  consequential or incidental,         particulier ou général,
# *  arising from the use of the          accessoire ou fortuit, résultant
# *  software.  Neither the name          de l'utilisation du logiciel. Ni
# *  of the National Research             le nom du Conseil National de
# *  Council of Canada nor the            Recherches du Canada ni les noms
# *  names of its contributors may        de ses  participants ne peuvent
# *  be used to endorse or promote        être utilisés pour approuver ou
# *  products derived from this           promouvoir les produits dérivés
# *  software without specific prior      de ce logiciel sans autorisation
# *  written permission.                  préalable et particulière
# *                                       par écrit.
# *
# *  This file is part of the             Ce fichier fait partie du projet
# *  OpenCADC project.                    OpenCADC.
# *
# *  OpenCADC is free software:           OpenCADC est un logiciel libre ;
# *  you can redistribute it and/or       vous pouvez le redistribuer ou le
# *  modify it under the terms of         modifier suivant les termes de
# *  the GNU Affero General Public        la “GNU Affero General Public
# *  License as published by the          License” telle que publiée
# *  Free Software Foundation,            par la Free Software Foundation
# *  either version 3 of the              : soit la version 3 de cette
# *  License, or (at your option)         licence, soit (à votre gré)
# *  any later version.                   toute version ultérieure.
# *
# *  OpenCADC is distributed in the       OpenCADC est distribué
# *  hope that it will be useful,         dans l’espoir qu’il vous
# *  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
# *  without even the implied             GARANTIE : sans même la garantie
# *  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
# *  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
# *  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
# *  General Public License for           Générale Publique GNU Affero
# *  more details.                        pour plus de détails.
# *
# *  You should have received             Vous devriez avoir reçu une
# *  a copy of the GNU Affero             copie de la Licence Générale
# *  General Public License along         Publique GNU Affero avec
# *  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
# *  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
# *                                       <http://www.gnu.org/licenses/>.
# *
# ************************************************************************

# Client for interaction with the CANFAR proc service

import logging
import os
import re
import uuid

import glanceclient.v2.client as glclient
import keystoneclient.v2_0.client as ksclient
import novaclient.client as nclient
from canfar.common.client import BaseClient
from glanceclient.exc import HTTPConflict
from requests.auth import HTTPBasicAuth


class ProcClient(BaseClient):
    """Class for interacting with CANFAR proc service"""

    def __init__(self, auth, *args, **kwargs):
        """proc service client constructor.

        auth -- Dict with OpenStack auth parameters: 'username', 'password',
                'tenant_name', 'auth_url'
        """

        # This client is special in that it uses OpenStack auth
        # parameters to communicate with OpenStack services, as well
        # as name/password authentication with the CANFAR proc
        # service. Note that the CANFAR username is assumed to be the
        # OpenStack username with a '-canfar' suffix removed.

        for key in ['username','password','tenant_name','auth_url']:
            if key not in auth:
                raise ValueError('auth dict does not contain %s' % key)
        self.auth = auth
        canfar_user = self.auth['username'].split('-canfar')[0]
        basic_auth = HTTPBasicAuth(canfar_user, self.auth['password'])
        super(ProcClient, self).__init__(usenetrc=False, certfile=None,
                                           basic_auth=basic_auth,
                                           *args, **kwargs)

        # Specific base_url for proc web service
        self.base_url = self.base_url + '/proc'

        # The batch tenant ID with which images need to be shared
        self.batch_tenant_id = '4267ed6832cd4a1f8d7057142fb36520'

        # Initialize the OpenStack clients. The token associated with
        # them will expire after an amount of time configured on the
        # server side, so in the event of a failure try
        # re-initializing them once.
        self._init_openstack_clients()

    def _make_logger(self):
        """ Logger for gmsclient """
        self.logger = logging.getLogger('procclient')

    def _init_openstack_clients(self):
        """Initialize OpenStack clients scoped to the current tenant.

        These clients use tokens that expire after a certain time, so
        call again in the event of a failure.
        """

        self.kclient = ksclient.Client(
            username=self.auth['username'],
            password=self.auth['password'],
            tenant_name=self.auth['tenant_name'],
            auth_url=self.auth['auth_url'] )

        glance_endpoint = self.kclient.service_catalog.url_for(
            service_type='image')

        self.gclient = glclient.Client(glance_endpoint,
                                       token=self.kclient.auth_token)
        self.nclient = nclient.Client(2, self.auth['username'],
                                      self.auth['password'],
                                      self.auth['tenant_name'],
                                      self.auth['auth_url'])

    def _resolve_image(self, image):
        """ Given an image (either name or ID) return (id,name) """

        try:
            # caller provided image_id
            image_id = str(uuid.UUID(image))
            image_name = None
        except:
            # caller provided image_name
            image_id = None
            image_name = image

        if not image_id:
            matches = []

            token_refreshed = False
            success = False
            while not success:
                try:
                    images = self.gclient.images.list()
                    success = True
                except:
                    if token_refreshed:
                        # We've tried a token refresh already so give up
                        raise
                    else:
                        # Refresh the token and try again
                        self._init_openstack_clients()
                        token_refreshed = True

            for im in images:
                if image_name == im['name']:
                    matches.append(im['id'])

            if len(matches) == 0:
                raise ValueError("Couldn't find image named '%s'" % image_name)
            elif len(matches) > 1:
                errstr="Multiple image IDs in tenant '%s' match image name '%s':\n%s"\
                    % (self.auth['tenant_name'], image_name, '\n'.join(matches))
                raise ValueError(errstr)
            else:
                # unique image_id
                image_id = matches[0]

        return image_id, image_name

    def _resolve_flavor(self, flavor):
        """ Given a flavor (either name or ID) return (id,name) """

        try:
            # user provided flavor_id
            flavor_id = str(uuid.UUID(flavor))
            flavor_name = None
        except:
            # user provided image_name
            flavor_id = None
            flavor_name = flavor

        if not flavor_id:

            token_refreshed = False
            success = False
            while not success:
                try:
                    flavors = self.nclient.flavors.list()
                    success = True
                except:
                    if token_refreshed:
                        # We've tried a token refresh already so give up
                        raise
                    else:
                        # Refresh the token and try again
                        self._init_openstack_clients()
                        token_refreshed = True

            for f in flavors:
                if flavor_name == f.name:
                    flavor_id = f.id
            if not flavor_id:
                flavor_names = [f.name for f in flavors]
                msg = "Supplied flavor '%s' is not valid. Must be one of:\n"\
                    % flavor
                msg = msg + ', '.join(flavor_names)
                raise ValueError(msg)

        return flavor_id, flavor_name


    def _share_image(self, image_id):
        """Share image with the batch tenant"""

        self.logger.warning("sharing image_id '%s' with batch tenant" % \
                                image_id)

        token_refreshed = False
        success = False
        while not success:
            try:
                self.gclient.image_members.create(image_id,self.batch_tenant_id)
                success = True
            except Exception as E:
                if isinstance(E, HTTPConflict):
                    if E.code == 409:
                        success = True
                        self.logger.warning("Image already shared.")
                        break

                if token_refreshed:
                    # We've tried a token refresh already so give up
                    raise
                else:
                    # Refresh the token and try again
                    self._init_openstack_clients()
                    token_refreshed = True


    def submit_job(self, jobfile, image, flavor, jobscriptonvm=None,
                   nopost=False):

        # Read in jobfile
        jobfile_data = open(jobfile,'r').read()

        # Search for the name of the job execution script in the Condor
        # job description file
        jobscript = None
        matches = re.findall("^\s*Executable\s*=\s*(.*)$",jobfile_data,
                             re.MULTILINE)

        if matches:
            if len(matches) > 1:
                raise ValueError(
                    "Multiple 'Executable' values in jobfile:\n%s" % \
                        '\n'.join(matches))
            elif jobscriptonvm:
                # Allow jobscriptonvm to override Executable line in jobfile
                jobscript = None
            else:
                jobscript = matches[0]
                jobscript_data = open(jobscript,'r').read()
        elif not jobscriptonvm:
            raise ValueError(
                "Must specify 'Executable' in jobfile or '--jobscriptonvm'")

        self.logger.warning(
'''auth_url: %s
username: %s
password: HIDDEN
tenant_name: %s
jobfile: %s
jobscript: %s''' % (self.auth['auth_url'],self.auth['username'],
                    self.auth['tenant_name'], jobfile, jobscript))

        # Resolve the caller's VM image and flavor, and share the
        # image with the batch tenant
        (image_id, image_name) = self._resolve_image(image)
        (flavor_id, flavor_name) = self._resolve_flavor(flavor)
        self._share_image(image_id)

        # Prepare and POST the job to the service.
        # See this stackoverflow post about how to send mulipart form
        # data in the POST with requests:
        # http://stackoverflow.com/questions/12385179/how-to-send-a-multipart-form-data-with-requests-in-python

        params = { 'image' : 'vmi:%s' % image_id,
                   'flavor': 'fli:%s' % flavor_id,
                   'job'   : 'job,param:job' }

        files = { 'job' : jobfile_data }

        if jobscriptonvm is not None:
            params['exec'] = '%s,vm:%s' \
                % (os.path.basename(jobscriptonvm),jobscriptonvm)
        else:
            params['exec'] = '%s,param:exec' \
                % os.path.basename(jobscript)
            files['exec'] = jobscript_data

        if nopost:
            self.logger.warning(
                "VM shared and flavor checks out, but --nopost requested. " +\
                    "The following will NOT be POSTed to the service:")
            for d in [params, files]:
                self.logger.warning("------------------------")
                for key in d:
                    self.logger.warning("+++%s+++\n%s" % (key,d[key]))
            # Useful outputs that can be fed to canfar_job_validate
            self.logger.warning("image_id and flavor_id:")
            print "%s %s" % (image_id,flavor_id)
        else:
            response = self._post(self.base_url+'/auth/job', params=params,
                                  files=files)
            if response.status_code == 400:
                # Display server message here before raising exception
                self.logger.error(
                    'Job submission failed. Server response:\n%s' % \
                        response.text)
            self.check_exception(response)
            self.logger.warning('Response from proc service (job cluster):')
            print response.text

