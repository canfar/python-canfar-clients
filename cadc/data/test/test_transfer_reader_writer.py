import os
import sys
import unittest
from lxml import etree

# put local code at start of path
sys.path.insert(0, os.path.abspath('../../../'))

from cadc.data.transfer import Transfer
from cadc.data.transfer import TransferError
from cadc.data.transfer_reader import TransferReader
from cadc.data.transfer_writer import TransferWriter
from cadc.data.protocol import Protocol
from cadc.data.constants import *

test_target_good = 'vos://cadc.nrc.ca~vospace/file'
test_target_bad = 'ftp://garbage/target'
test_dir_put = 'pushToVoSpace'
test_dir_get = 'pullFromVoSpace'
test_dir_bad = 'push'

class TestTransferReaderWriter(unittest.TestCase):

    def test_transfer_constructor(self):
        # target not of form vos: or ad:
        with self.assertRaises( TransferError ):
            Transfer( test_target_bad, test_dir_put )

        # invalid direction
        with self.assertRaises( TransferError ):
            Transfer( test_target_good, test_dir_bad )

        # protocol inconsistent with direction
        with self.assertRaises( TransferError ):
            Transfer( test_target_good, test_dir_put,
                      protocols=[
                    Protocol( DIRECTION_PROTOCOL_MAP['pullFromVoSpace'] ) ] )

        # invalid version
        with self.assertRaises( TransferError ):
            Transfer( test_target_good, test_dir_put, version=9999 )

        # invalid property
        with self.assertRaises( TransferError ):
            Transfer( test_target_good, test_dir_put,
                      protocols=[
                    Protocol( DIRECTION_PROTOCOL_MAP['pushToVoSpace'] ) ],
                      properties = {'LENGTH':'1234'} )

        # property can be set if using VOSPACE_21
        tran = Transfer( test_target_good, test_dir_put,
                         protocols=[
                Protocol( DIRECTION_PROTOCOL_MAP['pushToVoSpace'] ) ],
                         properties = {'LENGTH':'1234'},
                         version=VOSPACE_21 )

        self.assertEqual(tran.target, test_target_good,
                         'Wrong target.')
        self.assertEqual(1, len(tran.protocols), 'Wrong number of protocols.')
        self.assertEqual( tran.protocols[0].uri,
                          DIRECTION_PROTOCOL_MAP[test_dir_put],
                          'Wrong protocol URI' )
        self.assertEqual(VOSPACE_21, tran.version)
        self.assertEqual(1, len(tran.properties), 'Wrong number of properties')
        self.assertEqual('1234',tran.properties['LENGTH'])

        # The simplest constructor for a put automatically sets protocol
        tran = Transfer( test_target_good, test_dir_put )
        self.assertEqual(1, len(tran.protocols), 'Wrong number of protocols.')
        self.assertEqual( tran.protocols[0].uri,
                          DIRECTION_PROTOCOL_MAP[test_dir_put],
                          'Wrong protocol URI' )

        # For a get constructor protocol is not set
        tran = Transfer( test_target_good, test_dir_get )
        self.assertEqual( tran.protocols[0].uri,
                          DIRECTION_PROTOCOL_MAP[test_dir_get],
                          'Wrong protocol URI')

    def test_roundtrip_put(self):
        tran = Transfer( test_target_good, test_dir_put,
                         properties = {'LENGTH':'1234'},
                         version=VOSPACE_21 )
        xml_str = TransferWriter().write(tran)
        tran2 = TransferReader(validate=True).read(xml_str)

        self.assertEqual( tran.target, tran2.target, 'Wrong target.' )
        self.assertEqual( tran.direction, tran2.direction, 'Wrong direction.' )
        self.assertEqual( tran.properties, tran2.properties,
                          'Wrong properties.' )
        self.assertEqual(len(tran.protocols), len(tran2.protocols),
                             'Wrong number of protocols.')
        for i in range(len(tran.protocols)):
            p1 = tran.protocols[i]
            p2 = tran2.protocols[i]

            self.assertEqual( p1.uri, p1.uri, 'Wrong uri, protocol %i' % i )
            self.assertEqual( p1.endpoint, p1.endpoint,
                              'Wrong endpoint, protocol %i' % i )

    def test_roundtrip_get(self):
        tran = Transfer( test_target_good, test_dir_get,
                         protocols=[
                Protocol( DIRECTION_PROTOCOL_MAP['pullFromVoSpace'],
                          endpoint='http://somewhere') ],
                         properties = {'LENGTH':'1234',
                                       'uri=ivo://ivoa.net/vospace/core#quota' :
                                           '100' },
                         version=VOSPACE_21 )

        xml_str = TransferWriter().write(tran)
        tran2 = TransferReader(validate=True).read(xml_str)

        self.assertEqual( tran.target, tran2.target, 'Wrong target.' )
        self.assertEqual( tran.direction, tran2.direction,
                          'Wrong direction.' )
        self.assertEqual( tran.properties, tran2.properties,
                          'Wrong properties.' )
        self.assertEqual(len(tran.protocols), len(tran2.protocols),
                         'Wrong number of protocols.')
        for i in range(len(tran.protocols)):
            p1 = tran.protocols[i]
            p2 = tran2.protocols[i]

            self.assertEqual( p1.uri, p1.uri, 'Wrong uri, protocol %i' % i )
            self.assertEqual( p1.endpoint, p1.endpoint,
                              'Wrong endpoint, protocol %i' % i )

    def test_validation(self):
        # VOSPACE_20
        tran = Transfer( test_target_good, test_dir_put,
                         version=VOSPACE_20 )
        xml_str = TransferWriter().write(tran)
        tran2 = TransferReader(validate=True).read(xml_str)

        # VOSPACE_21
        tran = Transfer( test_target_good, test_dir_put,
                         properties = {'LENGTH':'1234'},
                         version=VOSPACE_21 )
        xml_str = TransferWriter().write(tran)

        # introduce an error that schema validation should catch
        xml = etree.fromstring(xml_str)
        junk = etree.SubElement(xml, 'junk')
        xml_str2 = etree.tostring(xml,encoding='UTF-8',pretty_print=True)

        # should not raise exception because validation turned off by default
        tran2 = TransferReader().read(xml_str2)

        # should now raise exception with validation turned on
        with self.assertRaises( etree.DocumentInvalid ):
            tran2 = TransferReader(validate=True).read(xml_str2)

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTransferReaderWriter)
    return unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run()
