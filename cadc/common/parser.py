import os
from argparse import ArgumentParser
import __version__

class BaseParser(ArgumentParser):
    """An ArgumentParser with some common things most CADC clients will want"""

    def __init__(self, *args, **kwargs):

        ArgumentParser.__init__(self, *args, **kwargs)

        self.add_argument('certfile', type=str,
                        help="location of your CADC security certificate file"
                            + " (default=$HOME/.ssl/cadcproxy.pem",
                            default=os.path.join(os.getenv("HOME", "."),
                                                 ".ssl/cadcproxy.pem"))
        self.add_argument('--version', action='version',
                          version=__version__.version)

        self.add_argument('--verbose', type=bool, default=True,
                          help='verbose messages')
        self.add_argument('--debug', type=bool, help='debug messages')
        self.add_argument('--quiet', type=bool, help='run quietly')
