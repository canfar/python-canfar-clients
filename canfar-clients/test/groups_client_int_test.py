#!/usr/bin/env python

""" Defines GroupsClientIntTest class """

import os
import sys
import unittest
import uuid

# put local code at top of the search path
sys.path.insert(0, os.path.abspath('../'))
from canfar.groups.client import GroupsClient
from canfar.groups.group import Group


class GroupsClientIntTest(unittest.TestCase):
    """
    sample usage:

    groups_client_int_test.py foo.cadc.dao.nrc.ca /usr/cadc/dev/admin/test-certificates/x509_CADCAuthtest1.pem

    """
    def init(self):
        self.host = sys.argv[1]
        self.cert_file = sys.argv[2]
        print 'host: ' + self.host
        print 'cert_file: ' + self.cert_file

        os.environ['AC_WEBSERVICE_HOST'] = self.host

    def get_group_id(self, name):
        return 'ALLOW-TEST-ac_ws-inttest-%s-%s' % (name, uuid.uuid4())

    def test_groups_client(self):
        self.init()

        # Use the first version for lots of debugging information
        #client = GroupsClient(self.cert_file, log_level=logging.DEBUG)
        client = GroupsClient(self.cert_file)

        # create a group
        expected = Group(self.get_group_id('py1'))
        expected.description = 'group description'
        print 'expected group {0}'.format(expected)

        try:
            client.create_group(expected)
        except Exception, e:
            self.fail('Error creating group because {0}'.format(repr(e)))

        # get the group
        try:
            actual = client.get_group(expected.group_id)
        except Exception, e:
            self.fail('Error getting group because {0}'.format(repr(e)))

        self.assertEqual(actual.group_id, expected.group_id, 'group_ids do not match')
        self.assertEqual(actual.description, expected.description, 'descriptions do not match')

        # update the group
        owner = actual.owner

        expected.description = 'new description'
        expected.user_members.add(owner)
        expected.user_admins.add(owner)

        # create a second test group
        group_member = Group(self.get_group_id('py2'))
        try:
            client.create_group(group_member)
        except Exception, e:
            self.fail('Error creating group because {0}'.format(repr(e)))
        print 'group member {0}'.format(group_member)

        expected.group_members.add(group_member)
        expected.group_admins.add(group_member)

        try:
            client.update_group(expected)
            actual = client.get_group(expected.group_id)
        except Exception, e:
            # self.fail('Error getting group because ' + repr(e))
            raise

        self.assertEqual(actual.group_id, expected.group_id, 'group_ids do not match')
        self.assertEqual(actual.description, expected.description, 'descriptions do not match')
        # self.assertEqual(actual.owner.user_id, expected.owner.user_id, 'owner user_ids do not match')

        self.assertEqual(len(actual.group_members), len(expected.group_members),
                         'number of group members does not match')
        self.assertEqual(next(iter(actual.group_members)).group_id, next(iter(expected.group_members)).group_id,
                         'group members do not match')

        self.assertEqual(len(actual.group_admins), len(expected.group_admins),
                         'number of group admin does not match')
        self.assertEqual(next(iter(actual.group_admins)).group_id, next(iter(expected.group_admins)).group_id,
                         'group admins do not match')

        self.assertEqual(len(actual.user_members), len(expected.user_members),
                         'number of user members does not match')
        self.assertEqual(next(iter(actual.user_members)).internal_id, next(iter(expected.user_members)).internal_id,
                         'user members do not match')

        self.assertEqual(len(actual.user_admins), len(expected.user_admins),
                         'number of user admins does not match')
        self.assertEqual(next(iter(actual.user_admins)).internal_id, next(iter(expected.user_admins)).internal_id,
                         'user admins do not match')

suite = unittest.TestLoader().loadTestsFromTestCase(GroupsClientIntTest)
unittest.TextTestRunner(verbosity=2).run(suite)
