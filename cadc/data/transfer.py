from urlparse import urlparse
from protocol import Protocol
from constants import *

class TransferError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Transfer(object):
    """
    VOSpace transfer job description
    """

    def __init__(self, target, direction, version=None, properties=None,
                 protocols=None):
        """ Initialize a Transfer description """
        self.target = None
        self.direction = None
        self.properties = dict()
        self.protocols = []

        if version is None:
            self.version = VOSPACE_20
        else:
            self.set_version(version)

        self.set_target(target)
        self.set_direction(direction)

        # Optional properties from dictionary
        if properties:
            for property in properties:
                self.set_property(property, properties[property])

        # Optionally set protocols
        if protocols:
            for protocol in protocols:
                self.add_protocol(protocol)
        elif self.direction == 'pushToVoSpace':
            # If we're doing a put and no protocol specified, set default
            self.add_protocol(
                Protocol( DIRECTION_PROTOCOL_MAP['pushToVoSpace'] ) )
        elif self.direction == 'pullFromVoSpace':
            # If we're doing a pull and no protocol specified, set default
            self.add_protocol(
                Protocol( DIRECTION_PROTOCOL_MAP['pullFromVoSpace'] ) )

    def set_version(self, version_in):
        """ Set a valid VOSpace version """
        if version_in in VOSPACE_SCHEMA:
            self.version = version_in
        else:
            raise TransferError("Invalid VOSpace version %i specified.")

    def set_target(self, target_in):
        """ Set target with basic validation """
        scheme = urlparse(target_in).scheme.lower()
        if scheme not in ['vos', 'ad']:
            raise TransferError(
                "Target should be of the form vos:... or ad:...")
        self.target = target_in

    def set_direction(self, direction_in):
        """ Set direction """

        if direction_in not in DIRECTION_PROTOCOL_MAP:
            raise TransferError("Direction %s must be one of: %s" % \
                                    ( direction_in,
                                      ', '.join( \
                        [k for k in DIRECTION_PROTOCOL_MAP]) ) )

        self.direction = direction_in

        def get_endpoints(self):
            """ Return ordered list of endpoints """

            return [ p.endpoint for p in self.protocols ]

    def add_protocol(self, protocol):
        """ Add to ordered list of protocols """

        assert isinstance(protocol, Protocol)

        if protocol.uri and \
                (protocol.uri != DIRECTION_PROTOCOL_MAP[self.direction]):
            raise TransferError(
                "Protocol URI, %s, incompatible with transfer direction, %s." \
                    % (protocol.uri, self.direction) )

        self.protocols.append(protocol)

    def get_property(self, property):
        """ Return a property """

        return self.properties[property]

    def set_property(self, property, value):
        """ Set a property. If a handled property, perform version check """

        if property in NODE_PROPERTIES:
            (key,val,ver) = NODE_PROPERTIES[property]
            if self.version < ver:
                raise TransferError(
                    "%s may only be set in VOSpace documents version >= %i" \
                        % (property,ver) )

        assert isinstance(value, basestring)

        self.properties[property] = value
