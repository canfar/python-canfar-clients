from transfer import Transfer
from lxml import etree
from constants import *

class TransferWriterError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TransferWriter(object):
    """
    Write a Transfer object to XML
    """

    def write(self, transfer):
        """ Generate an XML string """

        assert isinstance(transfer, Transfer)

        # Create the root node
        try:
            NS = VOSPACE_NS[transfer.version]  # namespace URI
            NSMAP = {'vos':NS}                 # map for document
            VOS = '{%s}' % NS                  # VOS namespace string

        except:
            raise TransferWriterError(
                'Unexpected transfer version %i encountered' \
                    % transfer.version )

        xml = etree.Element(VOS + 'transfer', nsmap=NSMAP)

        # Other required nodes
        target = etree.SubElement(xml, VOS + 'target', nsmap=NSMAP)
        target.text = transfer.target

        direction = etree.SubElement(xml, VOS + 'direction', nsmap=NSMAP )
        direction.text = transfer.direction

        # Protocols
        for p in transfer.protocols:
            attrib = { 'uri' : p.uri }

            protocol = etree.SubElement(xml, VOS + 'protocol', attrib=attrib,
                                        nsmap=NSMAP)
            if p.endpoint:
                endpoint = etree.SubElement(protocol, VOS + 'endpoint',
                                            nsmap=NSMAP)
                endpoint.text = p.endpoint

        # Properties
        for property in transfer.properties:
            try:
                (key,val,ver) = NODE_PROPERTIES[property]
            except:
                # An unhandled property. We need to split the string
                # into key/val
                (key,val) = property.split('=')

            attrib = {key : val }
            param = etree.SubElement(xml, VOS + 'param', attrib=attrib,
                                     nsmap=NSMAP)
            param.text = transfer.properties[property]

        return etree.tostring(xml,encoding='UTF-8',pretty_print=True)

