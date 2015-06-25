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
    """ Construct a Transfer object from XML source """

    def __init__(self, validate=False):
        self.validate = validate

    def read(self,xml_string):
        """ Read XML document string and return a Transfer object """

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
                # Try a reverse lookup to find handled NODE_PROPERTY
                property = NODE_PROPERTIES_LOOKUP[val]
                properties[property] = p.text
            except:
                properties['%s=%s' % (key,val)] = p.text


        # Create the transfer object
        return Transfer( target, direction, version=version,
                         properties=properties, protocols=protocols )
