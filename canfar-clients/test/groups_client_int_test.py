#!/usr/bin/env python

""" Defines GroupsClientIntTest class """

import os
import sys
import unittest
import uuid

# put local code at top of the search path
sys.path.insert(0, os.path.abspath('../'))
from canfar.groups.client import GroupsClient, UsersClient
from canfar.groups.group import Group
from canfar.groups.exceptions import MemberExistsException, MemberNotFoundException


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

    @staticmethod
    def get_group_id(name):
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

        # get a user to add as an admin member
        self.assertTrue(len(actual.owner.identities) > 0)
        identity = actual.owner.identities.pop()
        users_client = UsersClient(self.cert_file)
        try:
            owner = users_client.get_user(identity)
        except Exception, e:
            self.fail('Error getting user {0} because {1}'.format(identity, repr(e)))

        expected.description = 'new description'
        expected.user_admins.add(owner)

        # add user as user member
        try:
            client.add_user_member(identity, expected.group_id)
        except Exception, e:
            self.fail('Error adding user member because {0}'.format(repr(e)))

        # get the group and confirm membership
        try:
            actual = client.get_group(expected.group_id)
        except Exception, e:
            self.fail('Error getting group because {0}'.format(repr(e)))

        self.assertTrue(len(actual.user_members) == 1)
        actual_user = actual.user_members.pop()
        self.assertIn(identity, actual_user.identities)

        # add the user a second time, should throw MemberExistsException

        try:
            client.add_user_member(identity, expected.group_id)
        except Exception as e:
            self.assertTrue(isinstance(e, MemberExistsException))

        # remove the user member
        try:
            client.remove_user_member(identity, expected.group_id)
        except Exception, e:
            self.fail('Error removing user member because {0}'.format(repr(e)))

        # get the group and confirm membership
        try:
            actual = client.get_group(expected.group_id)
        except Exception, e:
            self.fail('Error getting group because {0}'.format(repr(e)))

        self.assertTrue(len(actual.user_members) == 0)

        # delete the user again, should throw MemberNotFoundException
        try:
            client.remove_user_member(identity, expected.group_id)
        except Exception as e:
            self.assertTrue(isinstance(e, MemberNotFoundException))

        # create a second test group
        group_member = Group(self.get_group_id('py2'))
        try:
            client.create_group(group_member)
        except Exception, e:
            self.fail('Error creating group because {0}'.format(repr(e)))
        print 'group member {0}'.format(group_member)

        expected.group_members.add(group_member)
        expected.group_admins.add(group_member)

        # writer = GroupWriter()
        # expected_xml = writer.write(expected)
        # print "expected:\n{0}".format(expected_xml)

        try:
            client.update_group(expected)
            actual = client.get_group(expected.group_id)
        except Exception, e:
            # self.fail('Error getting group because ' + repr(e))
            raise

        # actual_xml = writer.write(actual)
        # print "actual:\n{0}".format(actual_xml)

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
        # self.assertEqual(next(iter(actual.user_members)).internal_id, next(iter(expected.user_members)).internal_id,
        #                  'user members do not match')

        self.assertEqual(len(actual.user_admins), len(expected.user_admins),
                         'number of user admins does not match')
        self.assertEqual(next(iter(actual.user_admins)).internal_id, next(iter(expected.user_admins)).internal_id,
                         'user admins do not match')


class UsersClientIntTest(unittest.TestCase):
    """
    sample usage:

    users_client_int_test.py foo.cadc.dao.nrc.ca /usr/cadc/dev/admin/test-certificates/x509_CADCAuthtest1.pem

    """
    def init(self):
        self.host = sys.argv[1]
        self.cert_file = sys.argv[2]
        print 'host: ' + self.host
        print 'cert_file: ' + self.cert_file

        os.environ['AC_WEBSERVICE_HOST'] = self.host

    def test_users_client(self):
        self.init()

        # Since the UsersClient can't currently create a user, as a work around
        # we create a new group, get the group, and use the group owner as
        # the user to try and get using the user client.
        groups_client = GroupsClient(self.cert_file)
        group = Group(GroupsClientIntTest.get_group_id('py1'))

        try:
            groups_client.create_group(group)
        except Exception, e:
            self.fail('Error creating group because {0}'.format(repr(e)))

        # get the group
        try:
            group = groups_client.get_group(group.group_id)
        except Exception, e:
            self.fail('Error getting group because {0}'.format(repr(e)))

        # group owner as test user
        expected_user = group.owner

        users_client = UsersClient(self.cert_file)

        # get the user using each of the user identities
        for identity in expected_user.identities:
            try:
                actual_user = users_client.get_user(identity)
            except Exception, e:
                self.fail('Error getting user {0} because {1}'.format(identity, repr(e)))

            self.assertEqual(actual_user.internal_id, expected_user.internal_id)


suite = unittest.TestLoader().loadTestsFromTestCase(GroupsClientIntTest)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(UsersClientIntTest)
unittest.TextTestRunner(verbosity=2).run(suite)
