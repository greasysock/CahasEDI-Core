# Acknowledgment for incoming / outgoing edi to test for integrity
from .templates import x12_997
from .stream_handle import EdiHeader

class Ack:

    def __init__(self, to_ack : EdiHeader):
        self._to_ack = to_ack
        self._ack = None
        self._gen_ack()

    # Ack Generation method.
    def _gen_ack(self):
        pass

    # Gets 997 documents for given EdiHeader
    def get_ack(self):
        return self._ack


class AckEdiEngine(Ack):

    def __init__(self, to_ack : EdiHeader):
        Ack.__init__(self, to_ack)

    # Override base class to be made later, but EdiEngine is used for now.
    def _gen_ack(self):
        self._to_ack.get_all_bytes_lists()
