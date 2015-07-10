#!/usr/bin/env python
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

""" Defines TestClient class """
from mock import Mock, MagicMock, patch, mock_open, call
import unittest
import requests
import os
import sys
import copy
import __builtin__

# put local code at top of the search path
sys.path.insert(0, os.path.abspath('../../../'))

from cadc.data.client import DataClient
from cadc.data.transfer_reader import TransferReader
from cadc.data.transfer_writer import TransferWriter
from cadc.data.exceptions import TransferException
from canfar.common.exceptions import UnauthorizedException

test_archive = 'TEST'
test_localfile = 'foo.fits'
test_localfile2 = '/somewhere/newfile'
test_uri = 'ad:%s/%s' % (test_archive,test_localfile)
test_stream = 'default'

test_cert = 'cadcproxy.pem'
test_host = 'some.host'
test_base_url = 'https://'+test_host+'/data'
test_headers = {'content-type': 'text/xml'}
mock_session = Mock(spec=requests.Session())
mock_response = Mock(spec=requests.Response())
mock_transfer_reader = Mock(spec=TransferReader)
mock_transfer_writer = Mock(spec=TransferWriter)

test_endpoint1='http://endpoint1'
test_endpoint2='http://endpoint2'

class ClientForTest(DataClient):
    """Subclass of DataClient with some hacks"""

    def __init__(self, certfile):
        super(ClientForTest,self).__init__(certfile)
        self.host = test_host
        self.base_url = test_base_url
        self.certificate_file_location = test_cert
        #self.transfer_reader = mock_transfer_reader
        #self.transfer_writer = mock_transfer_writer

    @staticmethod
    def read_data(location):
        f = open(location, 'r')
        try:
            data = f.read()
            return data
        finally:
            f.close()

    def _create_session(self):
        self.session = mock_session


test_get_transfer_xml = ClientForTest.read_data('get_transfer.xml')
test_get_transfer_resp_xml = ClientForTest.read_data(
    'get_transfer_response.xml')

test_put_transfer_xml = ClientForTest.read_data('put_transfer.xml')
test_put_transfer_resp_xml = ClientForTest.read_data(
    'put_transfer_response.xml')


class TestClient(unittest.TestCase):

    def test_constructor(self):
        # default client, patch netrc to ensure no netrc found
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.side_effect = Exception('No netrc')
            c = DataClient()
        self.assertIsNone(c.certificate_file_location)
        self.assertIsNone(c.basic_auth)
        self.assertFalse(c.is_authorized)
        self.assertEqual(c.protocol,'http')
        self.assertEqual(c.chunk_size,1024)
        self.assertIsNotNone(c.transfer_reader)
        self.assertFalse(c.transfer_reader.validate)
        self.assertIsNotNone(c.transfer_writer)

        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.side_effect = Exception('No netrc')
            c = DataClient(schema_validate=True)
        self.assertTrue(c.transfer_reader.validate)


    @patch('os.path.isfile')           # fake loading cert
    @patch('requests.Session.post')    # fake posting transfer doc
    @patch('requests.put')             # fake putting the file
    @patch('__builtin__.open')         # fake source file for put
    def test_put_file(self,mock_open,mock_requests_put,mock_session_post,
                      mock_isfile):

        mock_file = MagicMock(spec=file)
        mock_open.return_value = mock_file

        c = DataClient(certfile=test_cert)
        self.assertTrue(c.is_authorized)

        #logger = c.get_logger(debug=True)

        # a couple of mocked responses to requests
        mock_response = Mock()
        mock_response.text = test_put_transfer_resp_xml
        mock_response.status_code = 200
        mock_response.history = [1]

        mock_response_fail = Mock()
        mock_response_fail.text = test_put_transfer_resp_xml
        mock_response_fail.status_code = 503
        mock_response_fail.history = [1]
        mock_response_fail.raise_for_status = Mock(
            side_effect=Exception('Failed.') )

        # make sure that transfer_file raises en error on bad inputs
        with self.assertRaises(ValueError):
            c.transfer_file(test_localfile)

        # We mock the client session POST response to return desired
        # XML with a list of endpoints. We then check that the post
        # was called with the correct values.
        # The "mock_requests_put" is called to actually put the data,
        # and we ensure it is called with the correct endpoint.
        #
        # We do the whole thing three times: first time specifying a uri,
        # second time specifying archive (filename for URI derived from
        # local filename), and finally specifying both archive and filename.
        for i in range(3):
            mock_session_post.return_value = mock_response
            mock_requests_put.return_value = mock_response

            if i is 0:
                c.transfer_file(test_localfile, uri=test_uri, is_put=True)
            elif i is 1:
                c.transfer_file(test_localfile, archive=test_archive,
                                is_put=True)
            else:
                c.transfer_file(test_localfile, archive=test_archive,
                                filename=test_localfile, is_put=True)

            mock_session_post.assert_called_once_with(c.base_url,
                                                      data=test_put_transfer_xml,
                                                      json=None, verify=False,
                                                      headers=test_headers)

            mock_requests_put.assert_called_once_with(test_endpoint1,
                                                      data=mock_file)

            mock_open.reset_mock()
            mock_requests_put.reset_mock()
            mock_session_post.reset_mock()
            mock_isfile.reset_mock()

        # Test specifying the stream
        mock_session_post.return_value = mock_response
        mock_requests_put.return_value = mock_response

        c.transfer_file(test_localfile, archive=test_archive,
                        filename=test_localfile, is_put=True,
                        stream=test_stream)

        expected_headers = copy.deepcopy(test_headers)
        expected_headers['X-CADC-Stream'] = test_stream

        mock_session_post.assert_called_once_with(c.base_url,
                                                  data=test_put_transfer_xml,
                                                  json=None, verify=False,
                                                  headers=expected_headers)

        mock_requests_put.assert_called_once_with(test_endpoint1,
                                                  data=mock_file)

        mock_open.reset_mock()
        mock_requests_put.reset_mock()
        mock_session_post.reset_mock()
        mock_isfile.reset_mock()

        # First PUT (endpoint1) returns a failed response. The second
        # PUT (endpoint2) will work
        mock_requests_put.side_effect = [mock_response_fail, mock_response]

        c.transfer_file(test_localfile, uri=test_uri, is_put=True)

        mock_session_post.assert_called_once_with(c.base_url,
                                                  data=test_put_transfer_xml,
                                                  json=None, verify=False,
                                                  headers=test_headers)

        mock_requests_put.assert_has_calls(
            [ call(test_endpoint1, data=mock_file),
              call(test_endpoint2, data=mock_file) ] )

        mock_open.reset_mock()
        mock_requests_put.reset_mock()
        mock_session_post.reset_mock()
        mock_isfile.reset_mock()

        # Both endpoints, and therefore the transfer, fail
        mock_requests_put.side_effect = [mock_response_fail,
                                          mock_response_fail]

        with self.assertRaises(TransferException):
            c.transfer_file(test_localfile, uri=test_uri, is_put=True)


        mock_session_post.assert_called_once_with(c.base_url,
                                                  data=test_put_transfer_xml,
                                                  json=None, verify=False,
                                                  headers=test_headers )

        mock_requests_put.assert_has_calls(
            [ call(test_endpoint1, data=mock_file),
              call(test_endpoint2, data=mock_file) ] )

        mock_open.reset_mock()
        mock_requests_put.reset_mock()
        mock_session_post.reset_mock()
        mock_isfile.reset_mock()

        # An anonymous put should raise an UnauthorizedException
        c.is_authorized = False

        with self.assertRaises(UnauthorizedException):
            c.transfer_file(test_localfile, uri=test_uri, is_put=True)


    @patch('os.path.isfile')           # fake loading cert
    @patch('requests.Session.post')    # fake posting transfer doc
    @patch('requests.get' )            # fake getting the file
    @patch('__builtin__.open')         # fake target file for get
    def test_get_file(self,mock_open,mock_requests_get,mock_session_post,
                      mock_isfile):

        mock_file = MagicMock(spec=file)
        mock_open.return_value = mock_file

        c = DataClient(certfile=test_cert)
        self.assertTrue(c.is_authorized)

        #logger = c.get_logger(debug=True)

        # a couple of mocked responses to requests
        mock_response = Mock()
        mock_response.text = test_get_transfer_resp_xml
        mock_response.status_code = 200
        mock_response.history = [1]

        mock_response_get = Mock()
        mock_response_get.text = test_get_transfer_resp_xml
        mock_response_get.status_code = 200
        mock_response_get.history = [1]
        mock_response_get.iter_content=Mock(return_value=[1])

        mock_response_get_fail = Mock()
        mock_response_get_fail.text = test_get_transfer_resp_xml
        mock_response_get_fail.status_code = 503
        mock_response_get_fail.history = [1]
        mock_response_get_fail.raise_for_status = Mock(
            side_effect=Exception('Failed.') )

        # We mock the client session POST response to return desired
        # XML with a list of endpoints. We then check that the post
        # was called with the correct values.
        # The "mock_requests_get" is called to actually get the data,
        # and we ensure it is called with the correct endpoint. It also
        # requires an "iter_content" method that returns an iterable
        # to simulate streaming.
        mock_session_post.return_value = mock_response
        mock_requests_get.return_value = mock_response_get
        c.transfer_file(test_localfile, uri=test_uri)

        mock_session_post.assert_called_once_with(c.base_url,
                                                  data=test_get_transfer_xml,
                                                  json=None, verify=False,
                                                  headers=test_headers)

        mock_requests_get.assert_called_once_with(test_endpoint1, stream=True)

        mock_open.reset_mock()
        mock_requests_get.reset_mock()
        mock_session_post.reset_mock()
        mock_isfile.reset_mock()

        # First GET (endpoint1) returns a failed response. The second
        # GET (endpoint2) will work
        mock_requests_get.side_effect = [mock_response_get_fail,
                                         mock_response_get]

        c.transfer_file(test_localfile, uri=test_uri)

        mock_session_post.assert_called_once_with(c.base_url,
                                                  data=test_get_transfer_xml,
                                                  json=None, verify=False,
                                                  headers=test_headers)

        mock_requests_get.assert_has_calls(
            [ call(test_endpoint1, stream=True),
              call(test_endpoint2, stream=True) ] )

        mock_open.reset_mock()
        mock_requests_get.reset_mock()
        mock_session_post.reset_mock()
        mock_isfile.reset_mock()

        # Both endpoints, and therefore the transfer, fail
        mock_requests_get.side_effect = [mock_response_get_fail,
                                         mock_response_get_fail]

        with self.assertRaises(TransferException):
            c.transfer_file(test_localfile, uri=test_uri)

        mock_session_post.assert_called_once_with(c.base_url,
                                                  data=test_get_transfer_xml,
                                                  json=None, verify=False,
                                                  headers=test_headers )

        mock_requests_get.assert_has_calls(
            [ call(test_endpoint1, stream=True),
              call(test_endpoint2, stream=True) ] )

        mock_open.reset_mock()
        mock_requests_get.reset_mock()
        mock_session_post.reset_mock()
        mock_isfile.reset_mock()


    @patch('os.path.isfile')           # fake loading cert
    @patch('requests.Session.head')    # fake head request
    def test_data_info_cert(self,mock_session_head, mock_isfile):

        c = DataClient(certfile=test_cert, host=test_host)
        self.assertTrue(c.is_authorized)

        # a mocked response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'key': 'value'}
        mock_response.history = [1]

        # Head request when we have a cert
        mock_session_head.return_value = mock_response
        c.data_info(test_archive, test_localfile)

        mock_session_head.assert_called_once_with(
            'https://%s/data/pub/%s/%s' % (test_host, test_archive,
                                           test_localfile), verify=False )

        mock_session_head.reset_mock()
        mock_isfile.reset_mock()

        # We can also handle the anonymous case here

        c = DataClient(host=test_host, anonymous=True)
        self.assertFalse(c.is_authorized)

        mock_session_head.return_value = mock_response
        c.data_info(test_archive, test_localfile)

        mock_session_head.assert_called_once_with(
            'http://%s/data/pub/%s/%s' % (test_host, test_archive,
                                          test_localfile), verify=False )

        mock_session_head.reset_mock()
        mock_isfile.reset_mock()


    @patch('netrc.netrc.authenticators') # fake loading .netrc
    @patch('requests.Session.head')      # fake head request
    def test_data_info_netrc(self,mock_session_head, mock_authenticator):

        c = DataClient(certfile=test_cert, host=test_host)
        self.assertTrue(c.is_authorized)

        # a mocked response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'key': 'value'}
        mock_response.history = [1]

        # Head request when we are using .netrc
        mock_session_head.return_value = mock_response
        c.data_info(test_archive, test_localfile)

        mock_session_head.assert_called_once_with(
            'http://%s/data/auth/%s/%s' % (test_host, test_archive,
                                           test_localfile), verify=False )

        mock_session_head.reset_mock()


def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run()
