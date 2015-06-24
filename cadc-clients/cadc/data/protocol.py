from constants import *

class Protocol(object):
    """
    Container for data transfer URIs (put/get) and endpoints (get)
    """

    def __init__(self, uri, endpoint=None):
        self.uri = uri
        if endpoint:
            self.endpoint = endpoint
        else:
            self.endpoint = None

