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

from urlparse import urlparse
from protocol import Protocol
from constants import *

class TransferError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Transfer(object):
    """ VOSpace transfer job description """

    def __init__(self, target, direction, version=None, properties=None,
                 protocols=None):
        """ Initialize a Transfer description

        target    -- URI of remote file
        direction -- pushToVoSpace or pullFromVoSpace
        """
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
        """ Set a valid VOSpace version with validation. """

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
        """ Set direction

        direction_in -- pushToVoSpace or pullFromVoSpace
        """

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
