#!/usr/bin/env python2.7
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

""" Defines TestClient class """
import mock
import unittest
import requests
import os
import sys
import logging
from copy import deepcopy

# put local code at top of the search path
sys.path.insert(0, os.path.abspath('../../../'))

from canfar.groups.client import GroupsClient, UsersClient
from canfar.groups.identity import Identity
from canfar.groups.group_xml.group_reader import GroupReader
from canfar.groups.group import Group
from canfar.groups.exceptions import MemberExistsException, MemberNotFoundException

test_certificate_name = "cadcproxy.pem"
test_x500_dn = 'C=ca,O=someorg,OU=someunit,CN=somebody'
test_http_username = 'somebody'
test_host = 'some.host'
test_base_url = 'https://%s/ac' % test_host
test_group_id = 'testgroup_for_somebody'
test_headers = {'content-type': 'text/xml'}
test_params = {'IDTYPE' : 'x500', 'ROLE' : 'member', 'ID' : test_x500_dn}
mock_session = mock.Mock(spec=requests.Session())
mock_response = mock.Mock(spec=requests.Response())

# XML test return documents and corresponding group ID sets
_XML0 = '<?xml version="1.0" encoding="UTF-8"?>\r\n<groups />\r\n'
_XML1 = '<?xml version="1.0" encoding="UTF-8"?>\r\n<groups>\r\n' + \
        '<group uri="ivo://cadc.nrc.ca/gms?groupA">\r\n</group>' + \
        '\r\n</groups>'
_XML2 = '<?xml version="1.0" encoding="UTF-8"?>\r\n<groups>\r\n' + \
        '<group uri="ivo://cadc.nrc.ca/gms?groupA">\r\n</group>' + \
        '<group uri="ivo://cadc.nrc.ca/gms?groupB">\r\n</group>' + \
        '\r\n</groups>'

groups0 = []
groups1 = [Group('groupA')]
groups2 = [Group('groupA'), Group('groupB')]


class GroupsClientForTest(GroupsClient):
    """Subclass of GroupsClient with some hacks"""

    def __init__(self, *args, **kwargs):
        super(GroupsClientForTest, self).__init__(*args, **kwargs)
        self.base_url = test_base_url
        self.certificate_file_location = test_certificate_name
        self.is_authorized = True
        self.current_user_dn = test_x500_dn

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

    def get_current_user_dn(self):
        return test_x500_dn


class UsersClientForTest(UsersClient):
    """Subclass of GroupsClient with some hacks"""

    def __init__(self, *args, **kwargs):
        super(UsersClientForTest, self).__init__(*args, **kwargs)
        self.base_url = test_base_url
        self.certificate_file_location = test_certificate_name
        self.is_authorized = True
        self.current_user_dn = test_x500_dn

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

    def get_current_user_dn(self):
        return test_x500_dn

test_create_group_xml = GroupsClientForTest.read_data('create_group.xml')
test_get_group_xml = GroupsClientForTest.read_data('get_group.xml')
test_get_user_xml = UsersClientForTest.read_data('get_user.xml')


class TestClient(unittest.TestCase):

    def test_create_group(self):
        c = GroupsClientForTest(test_certificate_name)

        try:
            c.create_group(None)
        except ValueError as e:
            # Good!
            self.assertEqual("Group cannot be None.", e.message,
                             "Wrong error message.")

        mock_put_response = mock.Mock(spec=requests.Response())
        reader = GroupReader()
        group = reader.read(test_create_group_xml)

        # 404 group not found
        # mock_put_response.status_code = 404
        # mock_put_response.text = 'Group not found'
        #
        # try:
        #     c.create_group(group)
        # except e:
        #     self.assertEqual('', e.message)

        mock_put_response.status_code = 200
        mock_session.put.return_value = mock_put_response
        c.create_group(group)

        self.assertTrue(mock_session.put.called, "PUT was never called.")
        mock_session.put.assert_called_with(test_base_url + "/groups",
                                            data=test_create_group_xml.
                                            replace('\r', ''),
                                            verify=False,
                                            headers=test_headers)

    def test_get_group(self):
        c = GroupsClientForTest(test_certificate_name)

        try:
            c.get_group('')
        except ValueError as e:
            # Good!
            self.assertEqual("Group ID cannot be None or empty.", e.message,
                             "Wrong error message.")

        mock_response.text = test_get_group_xml
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        g = c.get_group(test_group_id)

        self.assertIsNotNone(g, 'Group for %s is none' % test_group_id)
        self.assertEqual(g.group_id, test_group_id, "Wrong group ID.")
        mock_session.get.assert_called_with(test_base_url + "/groups/"
                                            + test_group_id, verify=False)

    def test_update_group(self):
        c = GroupsClientForTest(test_certificate_name)

        try:
            c.update_group(None)
        except ValueError as e:
            # Good!
            self.assertEqual("Group cannot be None.", e.message,
                             "Wrong error message.")

        mock_post_response = mock.Mock(spec=requests.Response())

        mock_post_response.status_code = 200
        mock_session.post.return_value = mock_post_response

        reader = GroupReader()
        group = reader.read(test_create_group_xml)

        c.update_group(group)

        self.assertTrue(mock_session.post.called, "POST was never called.")
        mock_session.post.assert_called_with(test_base_url + "/groups/" + \
                                                 group.group_id,
                                             data=test_create_group_xml.
                                             replace('\r', ''),
                                             verify=False,
                                             json=None,
                                             headers=test_headers)

    def test_add_user_member(self):
        c = GroupsClientForTest(test_certificate_name)

        try:
            c.add_user_member(None, None)
        except ValueError as e:
            # Good!
            self.assertEqual("User identity cannot be None.", e.message,
                             "Wrong error message.")

        try:
            c.add_user_member(Identity('foo', 'HTTP'), None)
        except ValueError as e:
            # Good!
            self.assertEqual("Group ID cannot be None or empty.", e.message,
                             "Wrong error message.")

        try:
            c.add_user_member(Identity('foo', 'HTTP'), '')
        except ValueError as e:
            # Good!
            self.assertEqual("Group ID cannot be None or empty.", e.message,
                             "Wrong error message.")

        mock_put_response = mock.Mock(spec=requests.Response())
        mock_put_response.status_code = 409
        mock_session.put.return_value = mock_put_response

        identity = Identity('foo', 'HTTP')
        group_id = 'bar'
        url = '{0}/groups/{1}/userMembers/{2}'.format(test_base_url, group_id, identity.name)
        parameters = {'idType': identity.type}

        try:
            c.add_user_member(identity, group_id)
        except Exception as e:
            self.assertTrue(isinstance(e, MemberExistsException))

        mock_put_response.status_code = 200
        mock_session.put.return_value = mock_put_response

        c.add_user_member(identity, group_id)

        self.assertTrue(mock_session.put.called, "PUT was never called.")
        mock_session.put.assert_called_with(url, params=parameters)

    def test_remove_user_member(self):
        c = GroupsClientForTest(test_certificate_name)

        try:
            c.remove_user_member(None, None)
        except ValueError as e:
            # Good!
            self.assertEqual("User identity cannot be None.", e.message,
                             "Wrong error message.")

        try:
            c.remove_user_member(Identity('foo', 'HTTP'), None)
        except ValueError as e:
            # Good!
            self.assertEqual("Group ID cannot be None or empty.", e.message,
                             "Wrong error message.")

        try:
            c.remove_user_member(Identity('foo', 'HTTP'), '')
        except ValueError as e:
            # Good!
            self.assertEqual("Group ID cannot be None or empty.", e.message,
                             "Wrong error message.")

        mock_delete_response = mock.Mock(spec=requests.Response())
        mock_delete_response.status_code = 404
        mock_session.delete.return_value = mock_delete_response

        identity = Identity('foo', 'HTTP')
        group_id = 'bar'
        url = '{0}/groups/{1}/userMembers/{2}'.format(test_base_url, group_id, identity.name)
        parameters = {'idType': identity.type}

        try:
            c.remove_user_member(identity, group_id)
        except Exception as e:
            self.assertTrue(isinstance(e, MemberNotFoundException))

        mock_delete_response.status_code = 200
        mock_session.delete.return_value = mock_delete_response

        c.remove_user_member(identity, group_id)

        self.assertTrue(mock_session.delete.called, "DELETE was never called.")
        mock_session.delete.assert_called_with(url, params=parameters)

    @mock.patch('os.path.isfile')           # fake loading cert
    @mock.patch('canfar.common.client.BaseClient.get_current_user_dn') # fake dn
    @mock.patch('requests.Session.get')     # fake get
    def test_get_membership(self, mock_session_get, mock_get_dn, mock_isfile):
        """
        :param mock_session:       The mock_session object.
        :return:
        """
        mock_response = mock.Mock()
        mock_response.text = _XML2
        mock_response.status_code = 200

        mock_get_dn.return_value = test_x500_dn

        c = GroupsClient(test_certificate_name, host=test_host)

        # no arguments: return full list of memberships
        mock_session_get.return_value = mock_response
        self.assertEqual(c.get_membership(), groups2)
        mock_session_get.assert_called_once_with(
            test_base_url + "/search?", verify=False, params=test_params)
        mock_session_get.reset_mock()

        # provide a group name
        mock_response.text = _XML1
        these_params = deepcopy(test_params)
        these_params['GROUPID'] = 'groupA'
        self.assertEqual(c.get_membership(group_id='groupA'), groups1)
        mock_session_get.assert_called_once_with(
            test_base_url + "/search?", verify=False, params=these_params)
        mock_session_get.reset_mock()

        # group for which we are not a member
        mock_response.text = _XML0
        these_params['GROUPID'] = 'foo'
        self.assertEqual(c.get_membership(group_id='foo'), groups0)
        mock_session_get.assert_called_once_with(
            test_base_url + "/search?", verify=False, params=these_params)
        mock_session_get.reset_mock()

    @mock.patch('os.path.isfile')           # fake loading cert
    @mock.patch('canfar.common.client.BaseClient.get_current_user_dn') # fake dn
    @mock.patch('requests.Session.get')     # fake get
    def test_is_member(self, mock_session_get, mock_get_dn, mock_isfile):
        """
        :param mock_session:       The mock_session object.
        :return:
        """

        mock_response = mock.Mock()
        mock_response.text = _XML0
        mock_response.status_code = 200

        mock_response2 = mock.Mock()
        mock_response2.text = _XML0
        mock_response2.status_code = 200

        mock_get_dn.return_value = test_x500_dn

        c = GroupsClient(test_certificate_name, host=test_host)

        these_params = deepcopy(test_params)

        # Not a member of group
        these_params['GROUPID'] = 'foo'
        mock_session_get.return_value = mock_response
        self.assertFalse(c.is_member('foo'))
        mock_session_get.assert_called_once_with(
            test_base_url + "/search?", verify=False, params=these_params)
        mock_session_get.reset_mock()

        # Member of single supplied group
        mock_response.text = _XML1
        these_params['GROUPID'] = 'groupA'
        self.assertTrue(c.is_member('groupA'))
        mock_session_get.assert_called_once_with(
            test_base_url + "/search?", verify=False, params=these_params)
        mock_session_get.reset_mock()

        # Member of one of a list of groups: success after checking first
        self.assertTrue(c.is_member(['groupA', 'bork']))
        mock_session_get.assert_called_once_with(
            test_base_url + "/search?", verify=False, params=these_params)
        mock_session_get.reset_mock()

        # Member of one of a list of groups: 2 calls, success on second
        these_params2 = deepcopy(test_params)
        these_params2['GROUPID'] = 'bork'
        mock_session_get.side_effect = [mock_response2, mock_response]
        self.assertTrue(c.is_member(['bork','groupA']))
        mock_session_get.assert_has_calls(
            [ mock.call(test_base_url + "/search?", verify=False,
                        params=these_params2),
              mock.call(test_base_url + "/search?", verify=False,
                        params=these_params) ] )
        mock_session_get.reset_mock()

    def test_get_user(self):
        c = UsersClientForTest(test_certificate_name)

        try:
            c.get_user(None)
        except ValueError as e:
            # Good!
            self.assertEqual("User Identity cannot be None.", e.message, "Wrong error message: " + e.message)

        try:
            c.get_user('foo')
        except ValueError as e:
            self.assertEqual("identity must be of type Identity.", e.message, "Wrong error message: " + e.message)

        mock_response.text = test_get_user_xml
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        identity = Identity('foo', 'HTTP')
        u = c.get_user(identity)

        self.assertIsNotNone(u, 'User for %s is none' % Identity)
        self.assertTrue(identity in u.identities)
        mock_session.get.assert_called_with(test_base_url + "/users/foo?idType=HTTP", verify=False)


def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run()
