# Invoice
# Based on X12 004010 V1 Variant 10

from . import generic, template_operators
from .tags import _ISA, _IEA, _GS, _GE, _ST, _SE
import io

desc = "Invoice"
i = 810

def clean_lower_byte_head(bytes_list : list):
    return bytes_list[0].strip(b' \t\n\r\v\f').lower()


# Class contains headers for interchange, and content body
# TODO: Add/Remove content from file. Generate dictionary of all available options.
class AnsiX12StructureHeader:
    def __init__(self):

        # Interchange Header/Trailer
        self._isa = _ISA()
        self._iea = _IEA()
        self._bytes_list = None
        # AnsiX12StructureContent list which contains main body of message
        self._content = list()

    # Sets header and trailer based on
    # TODO: Error handling/Integrity Checking.
    def put_edi_data_bytes_list(self, bytes_list : list):
        self._bytes_list = bytes_list
        isa = None
        iea = None
        bytes_content_list = 0
        for data in self._bytes_list:
            head = clean_lower_byte_head(data)
            if head == b'isa':
                isa = data[1:]
            elif head == b'iea':
                iea = data[1:]
        self._isa.put_bytes_list(isa)
        self._iea.put_bytes_list(iea)

        for i,data in enumerate(self._bytes_list):
            head = clean_lower_byte_head(data)
            if head == b'gs':
                j = None
                for k,n_data in enumerate(self._bytes_list[i:]):
                    n_head = n_data[0].strip(b' \t\n\r\v\f').lower()
                    if n_head == b'ge':
                        j = k+i+1
                        break
                struct = AnsiX12StructureContent()
                struct.put_edi_data_bytes_list(self._bytes_list[i:j])
                self._content.append(struct)


# Class contains content for each
class AnsiX12StructureContent:
    def __init__(self):

        self._bytes_list = None

        # Group Header/Trailer
        self._gs = _GS()
        self._ge = _GE()

        # Transaction Set Header/Trailer
        self._st = _ST()
        self._se = _SE()

    def put_edi_data_bytes_list(self, bytes_list : list):

        self._bytes_list = bytes_list
        for data in self._bytes_list:
            head = clean_lower_byte_head(data)
            if head == b'gs':

                self._gs.put_bytes_list(data[1:])
            elif head == b'ge':
                self._ge.put_bytes_list(data[1:])
            elif head == b'st':
                self._st.put_bytes_list(data[1:])
            elif head == b'se':
                self._se.put_bytes_list(data[1:])
            else:
                print(head)

class Template(generic.Template):
    def __init__(self, edi_file: io.BytesIO):
        self._edi_file = edi_file
        generic.Template.__init__(self, self._edi_file, i, desc)
        self._x12_handler = AnsiX12StructureHeader()
        self._x12_handler.put_edi_data_bytes_list(self._to_bytes_array())


class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()