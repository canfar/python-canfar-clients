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

# Python implementation of the GMS client. Only supports x509 as the
# IDTYPE at present.

import logging
import os

import exceptions
from canfar.common.client import BaseClient
from canfar.groups.identity import Identity
from group_xml.group_reader import GroupReader
from group_xml.group_writer import GroupWriter
from group_xml.groups_reader import GroupsReader
from group_xml.user_reader import UserReader
from role import Role


class GroupsClient(BaseClient):
    """Class for interacting with the access control web service"""

    def __init__(self, *args, **kwargs):
        """GMS client constructor. The dn will be extracted from the
        x509 cert and available as a default for user_id in other
        method calls.

        certfile -- Path to CADC proxy certificate
        """

        # This client does not support name/password authentication
        super(GroupsClient, self).__init__(usenetrc=False, *args, **kwargs)

        # Specific base_url for AC webservice
        host = os.getenv('AC_WEBSERVICE_HOST', self.host)
        path = os.getenv('AC_WEBSERVICE_PATH', '/ac')
        self.base_url = '%s://%s%s' % ('https', host, path)
        self.logger.info('Base URL ' + self.base_url)

        # This client will need the user DN
        self.current_user_dn = self.get_current_user_dn()

        # Specialized exceptions handled by this client
        self._HTTP_STATUS_CODE_EXCEPTIONS[404] = {
            "User": exceptions.UserNotFoundException(),
            "Group": exceptions.GroupNotFoundException(),
            "Member": exceptions.MemberNotFoundException()
            }
        self._HTTP_STATUS_CODE_EXCEPTIONS[409] = {
            "Group": exceptions.GroupExistsException(),
            "Member": exceptions.MemberExistsException()
        }

    def create_group(self, group):
        """ Persist the given Group """
        if group is None:
            raise ValueError("Group cannot be None.")

        url = self.base_url + "/groups"
        writer = GroupWriter()
        xml_string = writer.write(group)
        self._upload_xml(url, xml_string, 'PUT')
        self.logger.info('Created group ' + group.group_id)

    def get_group(self, group_id):

        if group_id is None or group_id.strip() == '':
            raise ValueError("Group ID cannot be None or empty.")

        url = self.base_url + "/groups/" + group_id
        xml_string = self._download_xml(url)
        reader = GroupReader()
        group = reader.read(xml_string)
        self.logger.info('Retrieved group {0}'.format(group.group_id))
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
        self._upload_xml(url, xml_string, 'POST')
        self.logger.info('Updated group ' + group.group_id)

    def _make_logger(self):
        """ Logger for gmsclient """
        self.logger = logging.getLogger('gmsclient')

    def add_user_member(self, identity, group_id):
        """Add the user to the group's user members.

        identity - the user to add as a user member
        group_id - the group to add the user member
        """

        if identity is None:
            raise ValueError("User identity cannot be None.")
        if group_id is None or group_id.strip() == '':
            raise ValueError("Group ID cannot be None or empty.")

        url = '{0}/groups/{1}/userMembers/{2}'.format(self.base_url, group_id, identity.name)
        parameters = {'idType': identity.type}

        response = self._put(url, params=parameters)
        self.check_exception(response)

    def remove_user_member(self, identity, group_id):
        """Remove the user from the group's user members.

        identity - the user to remove as a user member
        group_id - the group to remove the user member
        """

        if identity is None:
            raise ValueError("User identity cannot be None.")
        if group_id is None or group_id.strip() == '':
            raise ValueError("Group ID cannot be None or empty.")

        url = '{0}/groups/{1}/userMembers/{2}'.format(self.base_url, group_id, identity.name)
        parameters = {'idType': identity.type}

        response = self._delete(url, params=parameters)
        self.check_exception(response)

    def get_membership(self, user_id=None, role=Role('member'),
                       group_id=None):
        """Search for user group membership, of a certain role.

        user_id -- if unspecified default to current_user_dn
        role -- Role
        group_id -- if specified search only for this group
        """

        if not user_id:
            user_id = self.current_user_dn

        url = self.base_url + "/search?"
        params = {'ID': user_id,
                  'IDTYPE': 'x500',
                  'ROLE': role.get_name()}
        if group_id:
            params['GROUPID'] = group_id

        xml_string = self._download_xml(url, params=params)
        reader = GroupsReader()
        groups = reader.read(xml_string)

        self.logger.info('Retrieved groups ' + ', '.join([g.group_id for g in groups]))

        return groups

    def is_member(self, group_ids, user_id=None, role=Role('member')):
        """ Return True if user_id is a member (type of role) of at
        least one group in group_ids. False otherwise.

        group_ids -- list of group ID strings
        user_id -- if unspecified default to x509_dn
        role -- Role
        """

        # Allow the caller to supply a single string
        if isinstance(group_ids, str):
            group_ids = [group_ids]

        if not user_id:
            user_id = self.current_user_dn

        # get_membership returns a single-element set if member of a
        # particular group. Stop as soon as we find one.
        for group in group_ids:
            if self.get_membership(group_id=group, user_id=user_id,
                                   role=role):
                return True

        return False


class UsersClient(BaseClient):
    """Class for interacting with the access control web service"""

    def __init__(self, *args, **kwargs):
        """GMS client constructor. The dn will be extracted from the
        x509 cert and available as a default for user_id in other
        method calls.

        certfile -- Path to CADC proxy certificate
        """

        # This client does not support name/password authentication
        super(UsersClient, self).__init__(usenetrc=False, *args, **kwargs)

        # Specific base_url for AC webservice
        host = os.getenv('AC_WEBSERVICE_HOST', self.host)
        path = os.getenv('AC_WEBSERVICE_PATH', '/ac')
        self.base_url = '%s://%s%s' % ('https', host, path)
        self.logger.info('Base URL ' + self.base_url)

        # This client will need the user DN
        self.current_user_dn = self.get_current_user_dn()

        # Specialized exceptions handled by this client
        self._HTTP_STATUS_CODE_EXCEPTIONS[404] = {
            "User": exceptions.UserNotFoundException(),
            "Group": exceptions.GroupNotFoundException()
        }
        self._HTTP_STATUS_CODE_EXCEPTIONS[409] = \
            exceptions.GroupExistsException()

    def get_user(self, identity):

        if identity is None:
            raise ValueError("User Identity cannot be None.")
        if not isinstance(identity, Identity):
            raise ValueError("identity must be of type Identity.")

        url = "{0}/users/{1}?idType={2}".format(self.base_url, identity.name, identity.type)
        xml_string = self._download_xml(url)
        reader = UserReader()
        user = reader.read(xml_string)
        self.logger.info('Retrieved user {0}'.format(user.internal_id))
        return user
