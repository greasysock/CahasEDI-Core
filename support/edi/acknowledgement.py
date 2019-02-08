# Acknowledgment for incoming / outgoing edi to test for integrity
from .templates import x12_997
from . import stream_handle
import subprocess, io

class Ack:

    def __init__(self, to_ack):
        self._to_ack = to_ack
        self._ack = None
        self._gen_ack()

    # Ack Generation method.
    def _gen_ack(self):
        pass

    # Gets 997 documents for given EdiHeader
    def get_ack(self):
        return self._ack


def get_cur_dir():
    out_stuff = __file__.split("/")[:-1]
    out_line = ""
    for folder in out_stuff:
        if folder != "":
            out_line += "/" + folder
    return out_line


class AckEdiEngine(Ack):
    _tool_name = get_cur_dir()+"/bin/release/netcoreapp2.2/linux-x64/editools"
    _separator = b'*'
    _terminator = b'~'
    def __init__(self, to_ack):
        Ack.__init__(self, to_ack)

    def _to_edi_form(self, all_bytes_list : list):
        out_memory = io.BytesIO()
        for section in all_bytes_list:
            out_line = b''
            for i,s in enumerate(section):

                if i+1 < section.__len__() and s:
                    out_line += s + self._separator
                elif s:
                    out_line += s + self._terminator
                elif not s:
                    if i + 1 < section.__len__():
                        out_line += self._separator
                    else:
                        out_line += self._terminator
            out_memory.write(out_line)
        out_memory.seek(0)
        return out_memory

    # Override base class to be made later, but EdiEngine is used for now.
    def _gen_ack(self):
        edi_file = self._to_edi_form(self._to_ack.get_all_bytes_lists())
        edi_bytes = edi_file.read()
        stuff = subprocess.run([self._tool_name], input=edi_bytes, stdout=subprocess.PIPE)
        if not stuff.stdout: return
        edi_997 = io.BytesIO()
        edi_997.write(stuff.stdout)
        edi_997.seek(0)
        self._ack = stream_handle.EdiFile(edi_997)
