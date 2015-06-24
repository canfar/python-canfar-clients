import netrc
import os
from argparse import ArgumentParser

class BaseParser(ArgumentParser):
    """An ArgumentParser with some common things most CADC clients will want"""

    def __init__(self, version=None, *args, **kwargs):

        ArgumentParser.__init__(self, *args, **kwargs)

        self.add_argument('--certfile', type=str,
                          help="location of your CADC security certificate file"
                          + " (default=$HOME/.ssl/cadcproxy.pem, " + \
                              "otherwise uses $HOME/.netrc for name/password)",
                          default=os.path.join(os.getenv("HOME", "."),
                                                 ".ssl/cadcproxy.pem"))
        self.add_argument('--anonymous', action="store_true", default=False,
                          help='Force anonymous connection, ' +
                          'ignoring certfile and .netrc entries')
        self.add_argument('--host', help="Base host for services"
                          + "(default=www.canfar.phys.uvic.ca")
        self.add_argument('--verbose', action="store_true", default=False,
                          help='verbose messages')
        self.add_argument('--debug', action="store_true", default=False,
                          help='debug messages')
        self.add_argument('--quiet', action="store_true", default=False,
                          help='run quietly')

        if version is not None:
            self.add_argument('--version', action='version',
                              version=version)

