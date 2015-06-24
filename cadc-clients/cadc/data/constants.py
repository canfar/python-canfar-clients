# VOSpace versions and schema (loaded as needed)
VOSPACE_20 = 20
VOSPACE_21 = 21
VOSPACE_SCHEMA = { VOSPACE_20 : None,
                   VOSPACE_21 : None }

# Other constants from the VOSpace standard
PROTOCOL_HTTP_GET = 'ivo://ivoa.net/vospace/core#httpget'
PROTOCOL_HTTP_PUT = 'ivo://ivoa.net/vospace/core#httpput'
DIRECTION_PROTOCOL_MAP = { 'pushToVoSpace' : PROTOCOL_HTTP_PUT,
                           'pullFromVoSpace' : PROTOCOL_HTTP_GET }

# The list of NODE_PROPERTIES is extensive. Any properties listed here are
# simply special ones that we plan to handle (e.g., length can only be set in
# > VOSPACE_21)
# Perhaps a new thing to add: md5? (to verify things without separate HEAD)
NODE_PROPERTIES = {
    'LENGTH' : ('uri','ivo://ivoa.net/vospace/core#length',VOSPACE_21)
    }

# Lookup NODE_PROPERTIES given the property value (e.g., URI)
NODE_PROPERTIES_LOOKUP = dict()
for property in NODE_PROPERTIES:
    (key,val,ver) = NODE_PROPERTIES[property]
    NODE_PROPERTIES_LOOKUP[val] = property

# XML-related constants
VOSPACE_NS = { VOSPACE_20 : 'http://www.ivoa.net/xml/VOSpace/v2.0',
               VOSPACE_21 : 'http://www.ivoa.net/xml/VOSpace/v2.1' }

VOSPACE_SCHEMA_RESOURCE = { VOSPACE_20 : 'VOSpace-2.0.xsd',
                            VOSPACE_21 : 'VOSpace-2.1.xsd' }
