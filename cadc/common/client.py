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

# Python client base class for interacting with CADC services. Main purpose
# is to provide common framework for authorization, logging, and RESTful
# interactions.

from OpenSSL import crypto
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# disable the unverified HTTPS call warnings
requests.packages.urllib3.disable_warnings()

_SSL_VERSION = 'TLSv1'

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

class BaseClient(object):
    """Base class for interacting with CADC services"""

    def __init__(self, certfile=None, username=None, password=None):
        """
        Client constructor

        certfile -- Path to CADC proxy certificate
        username -- User name (if using HTTPBasicAuth instead of certfile)
        password -- Password (if using HTTPBasicAuth instead of certfile)
        """

        self._make_logger()

        # Determine whether we are anonymous or authorized
        self.is_authorized = False
        self.certificate_file_location = None
        self.basic_auth = None

        if certfile is not None:
            self.certificate_file_location = certfile
            self.is_authorized = True

        if username is not None and password is not None:
            self.basic_auth = HTTPBasicAuth(username, password)
            self.is_authorized = True

        # Base URL for web services. Clients should append to this
        # URL the particular service path

        if self.is_authorized:
            self.protocol = 'https'
        else:
            self.protocol = 'http'

        self.host = 'www.canfar.phys.uvic.ca'
        self.base_url = '%s://%s' % (self.protocol, self.host)


        # Clients should add entries to this dict for specialized
        # conversion of HTTP error codes into particular exceptions.
        #
        # Use this form to include a search string in the response to
        # handle multiple possibilities:
        #     XXX : {'SEARCHSTRING1' : exceptionInstance1,
        #            'SEARCHSTRING2' : exceptionInstance2}
        #
        # Otherwise provide a simple HTTP code -> exception mapping
        #     XXX : exceptionInstance
        #
        # The actual conversion is performed by get_exception()
        self._HTTP_STATUS_CODE_EXCEPTIONS = dict()


    def get_current_user_dn(self):
        """
            Obtain the current user's DN from this client's certificate.  This
            will return a distinguished name, as it was read from the
            certificate.
            jenkinsd 2015.02.06
        """

        # Get the dn from the x509 cert
        self.logger.debug('Read dn from x509 cert {}'
                     .format(self.certificate_file_location))
        try:
            f = open(self.certificate_file_location, "r")
            certfile_data = f.read()
            f.close()
        except IOError, e:
            self.logger.error('Failed to read certfile: {}'.format(str(e)))
            raise

        try:
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, certfile_data)
            x509_dn = ""
            for part in x509.get_issuer().get_components():
                x509_dn = x509_dn + '='.join(part) + ','
            return x509_dn.rstrip(',')
        except crypto.Error, e:
            self.logger.error('Failed to parse certfile: {}'.format(str(e)))
            raise

    def _upload_xml(self, url, xml_string, method):
        """ PUT or POST XML string to URL, return the response """

        self.logger.debug('Uploading (%s) XML: %s' % (xml_string, method))

        s = self._create_session()
        if method == 'PUT':
            response = s.put(url, data=xml_string, verify=False)
        else:
            response = s.post(url, data=xml_string, json=None, verify=False)
        self.check_exception(response)

        return response

    def _download_xml(self, url):
        """ GET XML string from URL """
        self.logger.debug('Requesting XML: %s' % url)

        s = self._create_session()
        response = s.get(url, verify=False)
        self.check_exception(response)
        xml_string = response.text
        xml_string = xml_string.encode('utf-8')

        return xml_string

    def _create_session(self):
        self.logger.debug('Creating session.')

        s = requests.Session()
        s.mount('https://', SSLAdapter(_SSL_VERSION,
                                       self.certificate_file_location))
        return s

    def _make_logger(self):
        """ Override to initialize loggers for different clients """
        self.logger = logging.getLogger('cadcclient')

    def get_logger(self, verbose=True, debug=False, quiet=False):
        """ Set up and return logger """

        log_format = "%(module)s: %(levelname)s: %(message)s"

        log_level = ((debug and logging.DEBUG) or (verbose and logging.INFO) or
                     (quiet and logging.FATAL) or logging.ERROR)

        if log_level == logging.DEBUG:
            log_format = "%(levelname)s: @(%(asctime)s) - " \
                "%(module)s.%(funcName)s %(lineno)d: %(message)s"

        self.logger.setLevel(log_level)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(fmt=log_format))
        self.logger.addHandler(stream_handler)
        return self.logger

    def check_exception(self, response):
        """
        Raise an exception, if any, that represents the status of the
        response.

        Specific exceptions may be handled by adding to the
        self._HTTP_STATUS_CODE_EXCEPTIONS dictionary.

        Otherwise falls back to response.raise_for_status() for standard
        exceptions.

        :param response:    The requests response object.
        """

        status_code = response.status_code
        status_text = response.text

        self.logger.debug("Checking for code %d" % status_code)

        try:
            http_exception_obj = self._HTTP_STATUS_CODE_EXCEPTIONS[status_code]

            if isinstance(http_exception_obj, Exception):
                # Simple mapping from HTTP code to exception object
                raise http_exception_obj
            else:
                # Otherwise search response for matching string
                for searchstring in http_exception_obj:
                    if status_text.startswith(searchstring):
                        raise http_exception_obj[searchstring]

                # Couldn't figure this one out. Note in logs and raise
                # exception from response if there is one
                self.logger.debug(
                    "Unable to identify particular exception for %s" \
                        % status_code)
                response.raise_for_status()

        except KeyError:
            # There is no error, or this is an unhandled exception.
            # Obtain exception from response if there is one.
            response.raise_for_status()

