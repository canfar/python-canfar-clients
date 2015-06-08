# -*- coding: utf-8 -*-
# ************************************************************************
# *******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# **************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
# *
# *  (c) 2014.                            (c) 2014.
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
# *  $Revision: 4 $
# *
# ************************************************************************

# Python implementation of the GMS client. Only supports x509 as the
# IDTYPE at present.

from OpenSSL import crypto
import logging
import requests
import os
import exceptions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from groups.group_xml.group_reader import GroupReader
from groups.group_xml.group_writer import GroupWriter

# disable the unverified HTTPS call warnings
requests.packages.urllib3.disable_warnings()

logger = logging.getLogger('gmsclient')

_HTTP_STATUS_CODE_EXCEPTIONS = {
    404: {
        "USER": exceptions.UserNotFoundException(),
        "GROUP": exceptions.GroupNotFoundException()
    },
    409: exceptions.GroupExistsException(),
    401: exceptions.UnauthorizedException()
}
_SSL_VERSION = 'TLSv1'


def get_exception(response):
    """
    Obtain the exception, if any, that represents the status of the response.
    :param response:    The requests response object.
    :return:    Exception, or None.
    """

    status_code = response.status_code
    status_text = response.text

    logger.debug("Checking for code %d" % status_code)

    try:
        http_exception_obj = _HTTP_STATUS_CODE_EXCEPTIONS[status_code]
        if status_code == 404:
            if status_text.startswith('User'):
                err = http_exception_obj["USER"]
            else:
                err = http_exception_obj["GROUP"]
        else:
            err = http_exception_obj
    except KeyError:
        # Good!  No error.
        err = None

    return err


def get_logger(verbose=True, debug=False, quiet=False):
    """Sets up the logging for gmsclient"""

    log_format = "%(module)s: %(levelname)s: %(message)s"

    log_level = ((debug and logging.DEBUG) or (verbose and logging.INFO) or
                 (quiet and logging.FATAL) or logging.ERROR)

    if log_level == logging.DEBUG:
        log_format = "%(levelname)s: @(%(asctime)s) - " \
                     "%(module)s.%(funcName)s %(lineno)d: %(message)s"

    logger.setLevel(log_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(fmt=log_format))
    logger.addHandler(stream_handler)
    return logger


class SSLAdapter(HTTPAdapter):
    """An HTTPS Transport Adapter that uses an arbitrary SSL version."""

    def __init__(self, ssl_version=None, cert_filename=None, **kwargs):
        self.ssl_version = ssl_version
        self.cert = cert_filename

        super(SSLAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        logger.debug("Connecting using {}".format(self.cert))

        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       key_file=self.cert,
                                       cert_file=self.cert,
                                       ssl_version=self.ssl_version)


class Client:
    """Class for interacting with the access control web service"""

    def __init__(self, certfile=None):
        """GMS client constructor. The dn will be extracted from the
        x509 cert and available as a default for user_id in other
        method calls.

        certfile -- Path to CADC proxy certificate
        """
        host = os.getenv('AC_WEBSERVICE_HOST', 'www.canfar.phys.uvic.ca')
        path = os.getenv('AC_WEBSERVICE_PATH', '/ac')
        self.base_url = '{}://{}{}'.format('https', host, path)
        self.certificate_file_location = certfile
        self.current_user_dn = self.get_current_user_dn()

        logger.info('Base URL {}'.format(self.base_url))

    def get_current_user_dn(self):
        """
            Obtain the current user's DN from this client's certificate.  This
            will return a distinguished name, as it was read from the
            certificate.
            jenkinsd 2015.02.06
        """

        # Get the dn from the x509 cert
        logger.debug('Read dn from x509 cert {}'
                     .format(self.certificate_file_location))
        try:
            f = open(self.certificate_file_location, "r")
            certfile_data = f.read()
            f.close()
        except IOError, e:
            logger.error('Failed to read certfile: {}'.format(str(e)))
            raise

        try:
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, certfile_data)
            x509_dn = ""
            for part in x509.get_issuer().get_components():
                x509_dn = x509_dn + '='.join(part) + ','
            return x509_dn.rstrip(',')
        except crypto.Error, e:
            logger.error('Failed to parse certfile: {}'.format(str(e)))
            raise

    def create_group(self, group):
        """
            Persist the given Group
        """
        if group is None:
            raise ValueError("Group cannot be None.")

        url = self.base_url + "/groups"
        writer = GroupWriter()
        xml_string = writer.write(group)
        self._upload_create_xml(url, xml_string, 'PUT')
        logger.info('Created group {}'.format(group.group_id))

    def get_group(self, group_id):

        if group_id is None or group_id.strip() == '':
            raise ValueError("Group ID cannot be None or empty.")

        url = self.base_url + "/groups/" + group_id
        xml_string = self._download_xml(url)
        reader = GroupReader()
        group = reader.read(xml_string)
        logger.info('Retrieved group {}'.format(group.group_id))
        return group

    def update_group(self, group):
        """
            Persist the given Group
        """
        if group is None:
            raise ValueError("Group cannot be None.")

        url = self.base_url + "/groups/" + group.group_id
        writer = GroupWriter()
        xml_string = writer.write(group)
        self._upload_create_xml(url, xml_string, 'POST')
        logger.info('Updated group {}'.format(group.group_id))

    def _upload_create_xml(self, url, xml_string, method):
        logger.debug('Uploading XML: {}'.format(xml_string))

        s = self._create_session()
        if method == 'PUT':
            response = s.put(url, data=xml_string, verify=False)
        else:
            response = s.post(url, data=xml_string, json=None, verify=False)

        http_exception = get_exception(response)
        if http_exception is not None:
            raise http_exception

    def _download_xml(self, url):
        logger.debug('Requesting XML: {}'.format(url))

        s = self._create_session()
        response = s.get(url, verify=False)
        http_exception = get_exception(response)

        if http_exception is None:
            xml_string = response.text
            group_xml_string = xml_string.encode('utf-8')
            return group_xml_string
        else:
            raise http_exception

    def _create_session(self):
        logger.debug('Using cert at {}'.format(self.certificate_file_location))

        s = requests.Session()
        s.mount('https://', SSLAdapter(_SSL_VERSION, self.certificate_file_location))
        return s
