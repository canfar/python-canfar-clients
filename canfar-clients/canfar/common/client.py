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
# ************************************************************************

# Python client base class for interacting with CANFAR and CADC
# services.  Main purpose is to provide common framework for
# authorization, logging, and RESTful interactions.

from OpenSSL import crypto
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.auth import HTTPBasicAuth
from canfar.common import exceptions
import os.path
import netrc
import copy

# try to disable the unverified HTTPS call warnings
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass


_SSL_VERSION = 'TLSv1'

class SSLAdapter(HTTPAdapter):
    """An HTTPS Transport Adapter that uses an arbitrary SSL version."""

    def __init__(self, ssl_version=None, cert_filename=None, logger=None,
                 **kwargs):
        self.ssl_version = ssl_version
        self.cert = cert_filename
        self.logger = logger
        self.session = None

        super(SSLAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        if self.logger is not None:
            self.logger.debug("Connecting using " + self.cert)

        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       key_file=self.cert,
                                       cert_file=self.cert,
                                       ssl_version=self.ssl_version)

class BaseClient(object):
    """Base class for interacting with CADC services"""

    def __init__(self, certfile=None, anonymous=False, usenetrc=True,
                 basic_auth=None, host='www.canfar.phys.uvic.ca',
                 log_level=logging.ERROR):
        """
        Client constructor

        certfile  -- Path to CADC proxy certificate
        anonymous -- Force anonymous client, regardless of cert/.netrc
        usenetrc  -- Try to use name/password authentication?
        basic_auth-- An externally created HTTPBasicAuth object
        host      -- Override default service host
        log_level -- How verbose should the client's logger be
        """

        self._make_logger()
        self.setup_logger(log_level=log_level)
        self.host = host

        # Unless the caller specifically requests an anonymous client,
        # check first for a certificate, then an externally created
        # HTTPBasicAuth object, and finally a name+password in .netrc.
        self.is_authorized = False
        self.certificate_file_location = None
        self.basic_auth = None

        if not anonymous:
            if (certfile is not None) and (certfile is not ''):
                if os.path.isfile(certfile):
                    self.certificate_file_location = certfile
                    self.is_authorized = True
                else:
                    print "Unable to open supplied certfile '%s':" % certfile +\
                        " Ignoring."

            if not self.is_authorized:
                if basic_auth is not None:
                    self.basic_auth = basic_auth
                    self.is_authorized = True
                elif usenetrc:
                    try:
                        auth = netrc.netrc().authenticators(self.host)
                        username=auth[0]
                        password=auth[2]

                        self.basic_auth = HTTPBasicAuth(username, password)
                        self.is_authorized = True
                    except:
                        # .netrc check happens automatically, so no need for
                        # a message if it fails
                        pass

        self.logger.debug(
            "Client authorized: %s, certfile: %s, name/password: %s" % \
                (str(self.is_authorized), str(self.certificate_file_location),
                 str(self.basic_auth is not None)) )

        # Create a session
        self._create_session()

        # Base URL for web services.
        # Clients will probably append a specific service
        if self.certificate_file_location:
            self.protocol = 'https'
        else:
            # For both anonymous and name/password authentication
            self.protocol = 'http'

        self.base_url = '%s://%s' % (self.protocol, self.host)

        # Clients should add entries to this dict for specialized
        # conversion of HTTP error codes into particular exceptions.
        #
        # Use this form to include a search string in the response to
        # handle multiple possibilities for a single HTTP code.
        #     XXX : {'SEARCHSTRING1' : exceptionInstance1,
        #            'SEARCHSTRING2' : exceptionInstance2}
        #
        # Otherwise provide a simple HTTP code -> exception mapping
        #     XXX : exceptionInstance
        #
        # The actual conversion is performed by get_exception()
        self._HTTP_STATUS_CODE_EXCEPTIONS = {
            401 : exceptions.UnauthorizedException()
            }


    def get_current_user_dn(self):
        """ Obtain user distinguished name from client's certificate """

        if self.certificate_file_location is None:
            raise ValueError(
                'Unable to extract user DN because no cert provided')

        # Get the dn from the x509 cert
        self.logger.debug('Read dn from x509 cert ' + \
                              self.certificate_file_location)
        try:
            f = open(self.certificate_file_location, "r")
            certfile_data = f.read()
            f.close()
        except IOError, e:
            self.logger.error('Failed to read certfile: ' + str(e))
            raise

        try:
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, certfile_data)
            x509_dn = ""
            for part in x509.get_issuer().get_components():
                x509_dn = x509_dn + '='.join(part) + ','
            x509_dn = x509_dn.rstrip(',')
            self.logger.debug('Read X509 dn: %s' % x509_dn)
            return x509_dn.rstrip(',')
        except crypto.Error, e:
            self.logger.error('Failed to parse certfile: ' + str(e))
            raise

    def _post(self, *args, **kwargs):
        """Wrapper for POST so that we use this client's session"""
        return self.session.post(*args, **kwargs)

    def _put(self, *args, **kwargs):
        """Wrapper for PUT so that we use this client's session"""
        return self.session.put(*args, **kwargs)

    def _get(self, *args, **kwargs):
        """Wrapper for GET so that we use this client's session"""
        return self.session.get(*args, **kwargs)

    def _delete(self, *args, **kwargs):
        """Wrapper for DELETE so that we use this client's session"""
        return self.session.delete(*args, **kwargs)

    def _head(self, *args, **kwargs):
        """Wrapper for HEAD so that we use this client's session"""
        return self.session.head(*args, **kwargs)


    def _upload_xml(self, url, xml_string, method, headers=None):
        """ PUT or POST XML string to URL, return the response object

        url        -- where to send the string
        xml_string -- string containing xml
        method     -- PUT or POST
        headers    -- optional dictionary of HTTP headers
        """

        self.logger.debug('%s to (%s):\n%s' % (method, url, xml_string) )

        if headers is not None:
            local_headers = copy.deepcopy(headers)
        else:
            local_headers = dict()

        local_headers['content-type'] = 'text/xml'

        if method == 'PUT':
            response = self._put(url, data=xml_string, verify=False,
                                 headers=local_headers)
        elif method == 'POST':
            response = self._post(url, data=xml_string, json=None, verify=False,
                                 headers=local_headers)
        else:
            raise ValueError('Method must be PUT or POST')

        self.check_exception(response)

        return response

    def _download_xml(self, url, *args, **kwargs):
        """ GET XML string from URL """
        self.logger.debug('Requesting XML: %s' % url)

        response = self._get(url, verify=False, *args, **kwargs)

        self.logger.debug('Full request URL: %s' % response.url)

        self.check_exception(response)
        xml_string = response.text
        xml_string = xml_string.encode('utf-8')

        self.logger.debug('Retrieved XML string:\n%s' % xml_string)

        return xml_string

    def _head_request(self, url):
        """ Perform a HEAD request on URL and return response """
        response = self._head(url, verify=False)
        self.check_exception(response)

        return response

    def _create_session(self):
        self.logger.debug('Creating session.')

        # Note that the cert goes into the adapter, but we can also
        # use name/password for the auth. We may want to enforce the
        # usage of only the cert in case both name/password and cert
        # are provided.
        self.session = requests.Session()
        self.session.auth = self.basic_auth
        if self.certificate_file_location is not None:
            self.session.mount('https://',
                               SSLAdapter(_SSL_VERSION,
                                          self.certificate_file_location,
                                          logger=self.logger))

    def _make_logger(self):
        """ Override to initialize loggers for different clients """
        self.logger = logging.getLogger('cadcclient')

    def setup_logger(self, log_level=logging.ERROR):
        """ Setup logger. Default to ERROR level. """

        log_format = "%(module)s: %(levelname)s: %(message)s"

        if log_level == logging.DEBUG:
            log_format = "%(levelname)s: @(%(asctime)s) - " \
                "%(module)s.%(funcName)s %(lineno)d: %(message)s"

        self.logger.setLevel(log_level)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(fmt=log_format))
        self.logger.addHandler(stream_handler)

    def check_exception(self, response):
        """
        Raise an exception, if any, that represents the status of the
        response.

        Specific exceptions may be thrown by adding to the
        self._HTTP_STATUS_CODE_EXCEPTIONS dictionary.

        Otherwise falls back to response.raise_for_status() for standard
        exceptions.

        :param response:    The requests response object.
        """

        status_code = response.status_code
        try:
            status_text = response.text
        except RuntimeError as E:
            # This is to handle the case of a streamed get in which
            # case Requests will report
            # 'The content for this response was already consumed'
            status_text = ''
            pass

        self.logger.debug("Response code: %d" % status_code)
        if status_code != 200:
            self.logger.debug("Response text: %s" % status_text)

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

