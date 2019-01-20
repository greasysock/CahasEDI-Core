from .templates import generic,template_operators, x12_997, x12_860, x12_856, x12_855, x12_850, x12_810
from . import exceptions
import io
# Class for opening and assigning correct edi template to incoming and outgoing edi files for decoding/encoding on-the-fly


# TODO: implement feature to detect Terminator/Sub-Element Separator/Repeating Carrot

terminator = b'~'
sub_separator = b'>'
repeating = b'^'

class EdiFile:
    def __init__(self, edi_file : io.BytesIO):
        self._edi_file = edi_file
        self._assign_template()

    def _assign_template(self):
        lines = self._edi_file.readlines()
        out_bytes = b''
        for line in lines:
            line = line.rstrip(b'\n')
            out_bytes += line
        if out_bytes[0:3] != b'ISA':
            raise(exceptions.InvalidFileError(out_bytes[0:3]))
        self._separator = out_bytes[3:4]
        self._terminator = terminator
        self._sub_separator = sub_separator
        self._repeating = repeating

        sections = out_bytes.split(self._terminator)
        seperated_sections = list()
        for section in sections:
            seperated = section.split(self._separator)
            seperated_sections.append(seperated)

        self._identifier_code = b''
        for section in seperated_sections:
            if section[0] == b'ST':
                self._identifier_code = section[1]
                # TODO: Raise some error if code is invalid or not present.
        self._identifier_code = int(self._identifier_code)
        for template in template_operators.template_list:
            if template.identifier_code == self._identifier_code:
                self._template = template.get_template()
        self._edi_file.seek(0)
        self._template = self._template(self._edi_file)
        print(self._template)
