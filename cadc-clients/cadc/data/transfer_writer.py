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

from transfer import Transfer
from lxml import etree
from constants import *

class TransferWriterError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TransferWriter(object):
    """ Render a Transfer object as an XML string """

    def write(self, transfer):
        """ Generate an XML string from a Transfer object """

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

