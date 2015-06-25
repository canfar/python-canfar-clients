#!/usr/bin/env python2.7
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

test_cert = 'cadcproxy.pem'

# put local code at top of the search path
sys.path.insert(0, os.path.abspath('../../../'))

from canfar.common.client import BaseClient

class TestClient(unittest.TestCase):

    def test_constructor(self):
        # default client, patch netrc to ensure no netrc found
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.side_effect = Exception('No netrc')
            c = BaseClient()
        self.assertIsNone(c.certificate_file_location)
        self.assertIsNone(c.basic_auth)
        self.assertFalse(c.is_authorized)
        self.assertEqual(c.protocol,'http')

        # no certfile, but netrc works, so name+password auth
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.return_value = ['janedoe','account','password']
            c = BaseClient()
        self.assertIsNone(c.certificate_file_location)
        self.assertIsNotNone(c.basic_auth)
        self.assertTrue(c.is_authorized)
        self.assertEqual(c.protocol,'http')

        # certfile authorization, no netrc. Patch open as well so that
        # it appears to be successful
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.side_effect = Exception('No netrc')
            with patch('os.path.isfile') as mock_isfile:
                c = BaseClient(certfile=test_cert)
        self.assertEqual(c.certificate_file_location,test_cert)
        self.assertIsNone(c.basic_auth)
        self.assertTrue(c.is_authorized)
        self.assertEqual(c.protocol,'https')

        # bad certfile provided, no netrc, results in anonymous client
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.side_effect = Exception('No netrc')
            with patch('os.path.isfile') as mock_isfile:
                mock_isfile.return_value = False
                c = BaseClient(certfile=test_cert)
        self.assertIsNone(c.certificate_file_location)
        self.assertIsNone(c.basic_auth)
        self.assertFalse(c.is_authorized)
        self.assertEqual(c.protocol,'http')

        # bad certfile provided, good netrc results in authorized client
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            with patch('os.path.isfile') as mock_isfile:
                mock_isfile.return_value = False
                c = BaseClient(certfile=test_cert)
        self.assertIsNone(c.certificate_file_location)
        self.assertIsNotNone(c.basic_auth)
        self.assertTrue(c.is_authorized)
        self.assertEqual(c.protocol,'http')

        # cert and netrc are both provided. Only use cert
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.return_value = ['janedoe','account','password']
            with patch('os.path.isfile') as mock_isfile:
                c = BaseClient(certfile=test_cert)
        self.assertEqual(c.certificate_file_location,test_cert)
        self.assertIsNone(c.basic_auth)
        self.assertTrue(c.is_authorized)
        self.assertEqual(c.protocol,'https')

        # cert and netrc are both provided but request anonymous
        with patch('netrc.netrc.authenticators') as mock_authenticator:
            mock_authenticator.return_value = ['janedoe','account','password']
            with patch('os.path.isfile') as mock_isfile:
                c = BaseClient(certfile=test_cert,anonymous=True)
        self.assertIsNone(c.certificate_file_location)
        self.assertIsNone(c.basic_auth)
        self.assertFalse(c.is_authorized)
        self.assertEqual(c.protocol,'http')



def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run()
