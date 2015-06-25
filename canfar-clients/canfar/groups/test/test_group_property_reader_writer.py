#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
# (c) 2014.                            (c) 2014.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
# ***********************************************************************

import os
import sys
import unittest

# put local code at top of the search path
sys.path.insert(0, os.path.abspath('../../../'))

from canfar.groups.group_property import GroupProperty
from canfar.groups.group_xml.group_property_reader import GroupPropertyReader
from canfar.groups.group_xml.group_property_writer import GroupPropertyWriter


class TestGroupPropertyReaderWriter(unittest.TestCase):

    def test_group_reader_errors(self):
        reader = GroupPropertyReader()

        self.assertRaises(ValueError, reader.read, None)
        self.assertRaises(ValueError, reader.read, '')
        self.assertRaises(ValueError, reader.get_group_property, None)
        self.assertRaises(AttributeError, reader.get_group_property, '')

    def test_group_writer_errors(self):
        writer = GroupPropertyWriter()

        self.assertRaises(AssertionError, writer.write, None)
        self.assertRaises(AssertionError, writer.write, '')
        self.assertRaises(AttributeError, writer.get_property_element, None)
        self.assertRaises(AttributeError, writer.get_property_element, '')
        self.assertRaises(AttributeError, writer.get_property_element, None)


    def test_read_only_true(self):
        expected = GroupProperty('key', 'value', True)

        writer = GroupPropertyWriter()
        xml_string = writer.write(expected)

        self.assertIsNotNone(xml_string)
        self.assertTrue(len(xml_string) > 0)

        reader = GroupPropertyReader()

        actual = reader.read(xml_string)

        self.assertIsNotNone(actual)
        self.assertEqual(actual.key, expected.key)
        self.assertEqual(actual.value, expected.value)
        self.assertEqual(actual.read_only, expected.read_only)

    def test_read_only_false(self):
        expected = GroupProperty('key', 'value', False)

        writer = GroupPropertyWriter()
        xml_string = writer.write(expected)

        self.assertIsNotNone(xml_string)
        self.assertTrue(len(xml_string) > 0)

        reader = GroupPropertyReader()

        actual = reader.read(xml_string)

        self.assertIsNotNone(actual)
        self.assertEqual(actual.key, expected.key)
        self.assertEqual(actual.value, expected.value)
        self.assertEqual(actual.read_only, expected.read_only)



def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroupPropertyReaderWriter)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run()
