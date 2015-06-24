import os
from transfer import Transfer
from lxml import etree
from protocol import Protocol
from constants import *

class TransferReaderError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TransferReader(object):
    """
    Construct a Transfer object from XML source
    """

    def __init__(self, validate=False):
        self.validate = validate

    def read(self,xml_string):
        """
        Read Transfer from an XML document string
        """

        xml = etree.fromstring(xml_string)

        # Get the VOSpace version by performing a reverse name lookup
        # on the namespace string
        try:
            NS = xml.nsmap['vos']
            version = dict((v, k) for k, v in VOSPACE_NS.iteritems())[NS]
        except:
            raise TransferReaderError(
                'Unable to establish the VOSpace version of transfer document' )

        VOS = '{%s}' % NS                  # VOS namespace string

        # Schema validation now that we know the version
        if self.validate:
            if VOSPACE_SCHEMA[version] is None:
                # .xsd hasn't been loaded in yet
                filepath = os.path.dirname(__file__) + \
                    '/' + VOSPACE_SCHEMA_RESOURCE[version]

                try:
                    with open(filepath) as f:
                        schema_xml = etree.parse(f)
                        VOSPACE_SCHEMA[version] = etree.XMLSchema(schema_xml)
                except Exception as e:
                    raise TransferReaderError('Unable to load schema %s: %s' % \
                                                  (filepath, str(e)) )
            VOSPACE_SCHEMA[version].assertValid(xml)

        # Continue with required nodes
        try:
            target = xml.find(VOS + 'target').text
        except:
            raise TransferReaderError(
                'Unable to find a target in the transfer document' )

        try:
            direction = xml.find(VOS + 'direction').text
        except:
            raise TransferReaderError(
                'Unable to find direction in the transfer document' )

        # Protocols
        protocols=[]
        for p in xml.findall(VOS + 'protocol'):
            uri = p.attrib['uri']
            e = p.find(VOS + 'endpoint')
            if e is not None:
                endpoint = e.text
            else:
                endpoint = None
            protocols.append( Protocol( uri, endpoint=endpoint ) )

        # Properties
        properties = dict()
        for p in xml.findall(VOS + 'param'):
            # We only expect one key per parameter
            key = p.attrib.keys()[0]
            val = p.attrib[key]

            try:
                # Try a reverse lookup to find handledNODE_PROPERTY
                property = NODE_PROPERTIES_LOOKUP[val]
                properties[property] = p.text
            except:
                properties['%s=%s' % (key,val)] = p.text


        # Create the transfer object
        return Transfer( target, direction, version=version,
                         properties=properties, protocols=protocols )
