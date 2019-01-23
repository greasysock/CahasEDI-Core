from .templates import generic,template_operators, x12_997, x12_860, x12_856, x12_855, x12_850, x12_810
from .templates.tags import _ISA, _IEA, _GS, _GE
from . import exceptions
import io
# Class for opening and assigning correct edi template to incoming and outgoing edi files for decoding/encoding on-the-fly


# TODO: implement feature to detect Terminator/Sub-Element Separator/Repeating Carrot

terminator = b'~'
sub_separator = b'>'
repeating = b'^'


def clean_head(value : bytes):
    return value.strip(b' \t\n\r\v\f')


def discover_all_sections(start_head : bytes, end_head : bytes, bytes_list : list):
    found_list = list()
    # looping until all groups are found and added to list
    found = False
    start_i = 0
    offset = 0
    while not found:
        start_idx = None
        end_idx = None
        # TODO: Lots of integrity and error handling
        found_head = False
        for i, section in enumerate(bytes_list[start_i:]):
            if clean_head(section[0]) == start_head:
                start_idx = i + offset
                found_head = True
            elif clean_head(section[0]) == end_head and found_head:
                end_idx = i + offset
                break
        if start_idx != None and end_idx != None:
            start_i = start_idx + 1
            offset += start_i
            found_list.append(bytes_list[start_idx:end_idx + 1])
        else:
            found = True
    return found_list


"""
EDI Structure:

EdiHeader
    - EDI header and trailer content
    - Edi Groups (list)
        - Edi Group
            - Group header and trailer content
            - TemplateGroup (list)
                - x12_XXX.py (some template)
        - Edi Group
        
"""


class TemplateGroup(list):
    def append(self, obj:generic.Template):
        super().append(obj)


class EdiGroup:
    def __init__(self, init_data=None):
        self._GS = _GS()
        self._GE = _GE()
        self._template_group = TemplateGroup()
        if init_data is not None:
            self._init_group_data = init_data
            self._init_process()

    def _init_process(self):
        # Discover gs/ge
        gs = None
        ge = None

        for section in self._init_group_data:
            if clean_head(section[0]) == self._GS.tag:
                gs = section
            elif clean_head(section[0]) == self._GE.tag:
                ge = section

        if gs is not None:
            self._GS.put_bytes_list(gs[1:])
        if ge is not None:
            self._GE.put_bytes_list(ge[1:])

        # Discover all st/se
        find_list = discover_all_sections(b'ST', b'SE', self._init_group_data)
        for section in find_list:
            type = int(section[0][1])
            for template in template_operators.template_list:
                if template.identifier_code == type:
                    temp = template.get_template()
                    out = temp(section)
                    self._template_group.append(out)

class EdiGroups(list):
    def append(self, edi_group : EdiGroup):
        super().append(edi_group)


class EdiHeader:
    def __init__(self, init_data=None):
        self._ISA = _ISA()
        self._IEA = _IEA()
        self._edi_groups = EdiGroups()
        if init_data is not None:
            self._init_edi_file = init_data
            self._init_process()

    def _init_process(self):
        # Discover isa/iea
        isa = None
        iea = None

        for section in self._init_edi_file:
            if clean_head(section[0]) == self._ISA.tag:
                isa = section
            elif clean_head(section[0]) == self._IEA.tag:
                iea = section

        if isa is not None:
            self._ISA.put_bytes_list(isa[1:])
        if iea is not None:
            self._IEA.put_bytes_list(iea[1:])

        # discover all gs/ge Groups
        found_list = discover_all_sections(b'GS', b'GE', self._init_edi_file)

        for bytes_list in found_list:
            tmp = EdiGroup(bytes_list)
            self._edi_groups.append(tmp)


class EdiFile:
    def __init__(self, edi_file : io.BytesIO):
        self._edi_file = edi_file
        self._separator = b'*'
        self._terminator = terminator
        self._sub_separator = sub_separator
        self._repeating = repeating
        self._assign_obj()

    def _assign_obj(self):
        self._edi_file.seek(0)
        lines = self._edi_file.readlines()


        # Check for empty files, if empty assume user is writing edi file
        if lines != []:
            self._assign_read_mod()
        else:
            self._assign_write()

    def _assign_write(self):
        pass

    def _assign_read_mod(self):
        self._edi_file.seek(0)
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

        self._edi_header = EdiHeader(seperated_sections)


"""
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
"""