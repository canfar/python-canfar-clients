class TransferException(Exception):
    """Raised when a data transfer fails

    Attributes:
        msg  -- explanation
    """

    def __init__(self, msg=None):
        self.msg = msg
