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

import logging
import os
from argparse import ArgumentParser

class BaseParser(ArgumentParser):
    """An ArgumentParser with some common things most CADC clients will want"""

    def __init__(self, version=None, usecert=True, *args, **kwargs):
        """ Construct a basic parser

        version  -- a version number if desired
        usercert -- if Truem add '--certfile' argument
        """

        ArgumentParser.__init__(self, *args, **kwargs)

        if usecert:
            self.add_argument('--certfile', type=str,
                              help="location of your CADC security certificate "
                              + "file (default=$HOME/.ssl/cadcproxy.pem, " + \
                              "otherwise uses $HOME/.netrc for name/password)",
                          default=os.path.join(os.getenv("HOME", "."),
                                                 ".ssl/cadcproxy.pem"))
        self.add_argument('--anonymous', action="store_true", default=False,
                          help='Force anonymous connection')
        self.add_argument('--host', help="Base hostname for services"
                          + "(default=www.canfar.phys.uvic.ca",
                          default='www.canfar.phys.uvic.ca')
        self.add_argument('--verbose', action="store_true", default=False,
                          help='verbose messages')
        self.add_argument('--debug', action="store_true", default=False,
                          help='debug messages')
        self.add_argument('--quiet', action="store_true", default=False,
                          help='run quietly')

        if version is not None:
            self.add_argument('--version', action='version',
                              version=version)

    def get_log_level(self, args):
        """ Obtain a single logger level from parsed args """

        log_level = ((args.debug and logging.DEBUG) or
                     (args.verbose and logging.INFO) or
                     (args.quiet and logging.FATAL) or logging.ERROR)

        return log_level
