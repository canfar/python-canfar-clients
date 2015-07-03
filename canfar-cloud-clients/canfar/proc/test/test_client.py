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

from canfar.proc.client import ProcClient

test_host = 'some.host'
test_base_url = 'http://'+test_host+'/proc'
test_job_url = test_base_url+'/auth/job'
test_auth = { 'username' : 'jane-canfar',
              'password' : 'bla',
              'tenant_name' : 'science',
              'auth_url' : 'https://some.cloud:5000/v2.0' }
test_job_works = 'test_job_works.sub'
test_job_fails = 'test_job_fails.sub'
test_script = 'test_script.bash'
test_script_on_vm = 'test_script_on_vm.bash'
test_image_name = 'test_vm'
test_image_id = '09a64c22-1283-4d7b-a700-a8b8e24f5c36'
test_flavor_name = 'tasty'
test_flavor_id = '09a64c22-1283-4d7b-a700-a8b8e24f5c36'
test_job_id = '1234'

test_params_works = { 'image' : 'vmi:%s' % test_image_id,
                      'flavor': 'fli:%s' % test_flavor_id,
                      'job'   : 'job,param:job',
                      'exec'  : test_script+',param:exec'}
test_files_works = { 'job' : open(test_job_works,'r').read(),
                     'exec' : open(test_script,'r').read() }

test_params_on_vm = { 'image' : 'vmi:%s' % test_image_id,
                      'flavor': 'fli:%s' % test_flavor_id,
                      'job'   : 'job,param:job',
                      'exec'  : test_script_on_vm+',vm:'+test_script_on_vm}
test_files_on_vm = { 'job' : open(test_job_fails,'r').read() }


class TestClient(unittest.TestCase):

    @patch('keystoneclient.v2_0.client.Client')
    @patch('novaclient.client.Client')
    @patch('glanceclient.v2.client.Client')
    def test_constructor(self, mock_g, mock_n, mock_k):
        # Fail if incomplete auth supplied
        with self.assertRaises(ValueError):
            c = ProcClient( { 'username' : 'jane-canfar'} )

        # Normal creation
        c = ProcClient(test_auth)

        self.assertIsNone(c.certificate_file_location)
        self.assertIsNotNone(c.basic_auth)
        self.assertTrue(c.is_authorized)
        self.assertEqual(c.protocol,'http')

    @patch('requests.Session.post')              # fake posting to proc service
    @patch('keystoneclient.v2_0.client.Client')  # fake keystone client class
    @patch('novaclient.client.Client')           # fake nova client class
    @patch('glanceclient.v2.client.Client')      # fake glance client class
    def test_submit_job(self, mock_g, mock_n, mock_k, mock_session_post):

        # Mock OpenStack clients and response to POST
        mock_image = { 'name': test_image_name,
                       'id' : test_image_id }
        mock_gclient = Mock()
        mock_gclient.images = Mock()
        mock_gclient.images.list = Mock(return_value=[mock_image])
        mock_g.return_value = mock_gclient

        mock_flavor = Mock()
        mock_flavor.name = test_flavor_name
        mock_flavor.id = test_flavor_id
        mock_nclient = Mock()
        mock_nclient.flavors = Mock()
        mock_nclient.flavors.list = Mock(return_value=[mock_flavor])
        mock_n.return_value = mock_nclient

        mock_response = Mock()
        mock_response.text = test_job_id
        mock_response.status_code = 200
        mock_session_post.return_value = mock_response

        c = ProcClient(test_auth, host=test_host)

        # good submission using image and flavor names
        c.submit_job(test_job_works, test_image_name, test_flavor_name)
        mock_session_post.assert_called_once_with(
            test_job_url, params=test_params_works, files=test_files_works)

        mock_session_post.reset_mock()

        # good submission using image and flavor UUIDs
        c.submit_job(test_job_works, test_image_id, test_flavor_id)
        mock_session_post.assert_called_once_with(
            test_job_url, params=test_params_works, files=test_files_works)

        mock_session_post.reset_mock()

        # With nopost we should not do a POST
        c.submit_job(test_job_works, test_image_name, test_flavor_name,
                     nopost=True)
        self.assertEqual(mock_session_post.call_count, 0)

        # failed submission due to bad image name
        with self.assertRaises(ValueError):
            c.submit_job(test_job_works, 'bad_image', test_flavor_name)
        self.assertEqual(mock_session_post.call_count, 0)

        # failed submission due to bad flavor name
        with self.assertRaises(ValueError):
            c.submit_job(test_job_works, test_image_name, 'yucky')
        self.assertEqual(mock_session_post.call_count, 0)

        # failed submission because no Executable line in job file
        with self.assertRaises(ValueError):
            c.submit_job(test_job_fails, test_image_name, test_flavor_name)
        self.assertEqual(mock_session_post.call_count, 0)

        # works without Executable by specifying jobscriptonvm
        c.submit_job(test_job_fails, test_image_name, test_flavor_name,
                     jobscriptonvm=test_script_on_vm)
        mock_session_post.assert_called_once_with(
            test_job_url, params=test_params_on_vm, files=test_files_on_vm)

        mock_session_post.reset_mock()

    # For these tests we are posting a job that is valid from the client
    # point of view, but we have to handle problem responses from the server
    @patch('requests.Session.post')              # fake posting to proc service
    @patch('keystoneclient.v2_0.client.Client')  # fake keystone client class
    @patch('novaclient.client.Client')           # fake nova client class
    @patch('glanceclient.v2.client.Client')      # fake glance client class
    def test_server_response(self, mock_g, mock_n, mock_k, mock_session_post):

        # Mock OpenStack clients and response to POST
        mock_image = { 'name': test_image_name,
                       'id' : test_image_id }
        mock_gclient = Mock()
        mock_gclient.images = Mock()
        mock_im_list = Mock(return_value=[mock_image])
        mock_gclient.images.list = mock_im_list
        mock_gclient.image_members = Mock()
        mock_gclient.image_members.create = Mock()
        mock_g.return_value = mock_gclient

        mock_flavor = Mock()
        mock_flavor.name = test_flavor_name
        mock_flavor.id = test_flavor_id
        mock_fl_list = Mock(return_value=[mock_flavor])
        mock_nclient = Mock()
        mock_nclient.flavors = Mock()
        mock_nclient.flavors.list = mock_fl_list
        mock_n.return_value = mock_nclient

        mock_response = Mock()
        mock_response.text = test_job_id
        mock_response.status_code = 200
        mock_session_post.return_value = mock_response

        c = ProcClient(test_auth, host=test_host)

        # Failure on server side when trying to validate job
        mock_response_validate = Mock()
        mock_response_validate.text = 'Failed to validate job.'
        mock_response_validate.status_code = 400
        mock_response_validate.raise_for_status = Mock(
           side_effect=Exception('Failed.') )
        mock_session_post.return_value = mock_response_validate

        with self.assertRaises(Exception):
            c.submit_job(test_job_works, test_image_name, test_flavor_name)
        mock_session_post.assert_called_once_with(
            test_job_url, params=test_params_works, files=test_files_works)

        mock_session_post.return_value = mock_response
        mock_session_post.reset_mock()

        # glance client needs to be refreshed. First time it tries to obtain
        # an image list it fails. Second time it works.
        mock_gclient.images.list.side_effect = [Exception('Failed'),
                                                mock_im_list()]
        mock_gclient.images.list.reset_mock()
        mock_g.reset_mock()
        c.submit_job(test_job_works, test_image_name, test_flavor_name)
        self.assertEqual(mock_gclient.images.list.call_count, 2)
        # only one additional call to glance client constructor since it
        # was originally created with the ProcClient instance
        self.assertEqual(mock_g.call_count, 1)
        mock_session_post.assert_called_once_with(
            test_job_url, params=test_params_works, files=test_files_works)

        mock_gclient.images.list.side_effect = None
        mock_session_post.reset_mock()

        # nova client needs to be refreshed. First time it tries to obtain
        # a flavor list it fails. Second time it works.
        mock_nclient.flavors.list.side_effect = [Exception('Failed'),
                                                mock_fl_list()]
        mock_nclient.flavors.list.reset_mock()
        mock_n.reset_mock()
        c.submit_job(test_job_works, test_image_name, test_flavor_name)
        self.assertEqual(mock_nclient.flavors.list.call_count, 2)
        self.assertEqual(mock_n.call_count, 1)
        mock_session_post.assert_called_once_with(
            test_job_url, params=test_params_works, files=test_files_works)

        mock_nclient.flavors.list.side_effect = None
        mock_session_post.reset_mock()

        # glance client needs to be refreshed. First time it tries to
        # share an image it fails. Second time it works.
        mock_gclient.image_members.create.side_effect = [Exception('Failed'),
                                                         Mock()]
        mock_gclient.image_members.create.reset_mock()
        mock_g.reset_mock()
        c.submit_job(test_job_works, test_image_name, test_flavor_name)
        self.assertEqual(mock_gclient.image_members.create.call_count, 2)
        self.assertEqual(mock_g.call_count, 1)
        mock_session_post.assert_called_once_with(
            test_job_url, params=test_params_works, files=test_files_works)


def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run()
