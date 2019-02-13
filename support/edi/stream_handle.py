from .templates import generic,template_operators, x12_997, x12_860, x12_856, x12_855, x12_850, x12_810
from .templates.tags import _ISA, _IEA, _GS, _GE
from . import exceptions
import io, datetime
from . import acknowledgement, group_identifiers

# Classes for opening and assigning correct edi template to incoming
# and outgoing edi files for decoding/encoding on-the-fly
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


class PartnershipData:

    def __init__(self, id_qualifier, my_id, partner_qualifier, partner_id):
        self._id_qualifier = id_qualifier
        self._id = my_id
        self._partner_qualifier = partner_qualifier
        self._partner_id = partner_id
        self._interchange_counter = 0
        self._group_counter = 0
        self._set_counter = 0

    @property
    def id_qualifier(self):
        return self._id_qualifier
    @property
    def id(self):
        return self._id
    @property
    def partner_qualifier(self):
        return self._partner_qualifier
    @property
    def partner_id(self):
        return self._partner_id

    def set_interchange_counter_method(self, method: classmethod):
        self._interchange_counter = method
    @property
    def interchange_counter(self):
        if type(self._interchange_counter) == int:
            self._interchange_counter += 1
            return self._interchange_counter
        return self._interchange_counter()

    def set_group_counter_method(self, method: classmethod):
        self._group_counter = method
    @property
    def group_counter(self):
        if type(self._group_counter) == int:
            self._group_counter += 1
            return self._group_counter
        return self._group_counter()

    def set_set_counter_method(self, method: classmethod):
        self._set_counter = method
    @property
    def set_counter(self):
        if type(self._set_counter) == int:
            self._set_counter += 1
            return self._set_counter
        return self._set_counter()


class GroupTransaction:
    def __init__(self, partnership: PartnershipData, functional_code:bytes, responsible_agency=b'X', version=b'004010'):
        self._partner = partnership
        self._functional_id = functional_code
        self._responsible_agency = responsible_agency
        self._control = str(self._partner.group_counter).encode()
        self._version = version

    def _get_time_big(self):
        time = datetime.datetime.now()
        return time.strftime("%Y%m%d").encode()

    def _get_time_little(self):
        time = datetime.datetime.now()
        return time.strftime("%H%M").encode()

    def get_bytes_list_gs(self):
        return [
            self._functional_id,
            self._partner.id.encode(),
            self._partner.partner_id.encode(),
            self._get_time_big(),
            self._get_time_little(),
            self._control,
            self._responsible_agency,
            self._version
        ]

    def get_bytes_list_ge(self, amount:int):
        return [
            str(amount).encode(),
            self._control
        ]

    def get_gs(self):
        gs = _GS()
        gs.put_bytes_list(self.get_bytes_list_gs())
        return gs

    @property
    def control_num(self):
        return int(self._control)

    def get_ge(self, amount:int):
        ge = _GE()
        ge.put_bytes_list(self.get_bytes_list_ge(amount))
        return ge


class InterchangeTransaction:
    def __init__(self, partnership: PartnershipData, usage_indicator = "T", interchg_ctr_ver_nmb="00400",interchg_stds = "U",comp_sep = '>'):
        self._partner = partnership
        self._interchg_stds = interchg_stds
        self._comp_sep = comp_sep
        self._interchg_ctr_ver_nmb = interchg_ctr_ver_nmb
        self._acknowledgment = False
        self._usage_indicator = usage_indicator
        self._auth_info_qualifier = "  "
        self._auth_info = "          "
        self._sec_info_qualifier = "  "
        self._sec_info = "          "
        self._ctr_number = self._partner.interchange_counter
        self._ISA = self.get_isa()
        self.edi_header = EdiHeader()
        self.edi_header.ISA = self._ISA

    def _get_time_big(self):
        time = datetime.datetime.now()
        return time.strftime("%y%m%d").encode()

    def _get_time_little(self):
        time = datetime.datetime.now()
        return time.strftime("%H%M").encode()

    @property
    def acknowledge(self):
        if self._acknowledgment:
            return "1"
        else:
            return "0"

    # build ISA
    def get_bytes_list_isa(self):
        return [
            self._auth_info_qualifier.encode(),
            self._auth_info.encode(),
            self._sec_info_qualifier.encode(),
            self._sec_info.encode(),
            self._partner.id_qualifier.encode(),
            self._partner.id.encode(),
            self._partner.partner_qualifier.encode(),
            self._partner.partner_id.encode(),
            self._get_time_big(),
            self._get_time_little(),
            self._interchg_stds.encode(),
            self._interchg_ctr_ver_nmb.encode(),
            str(self._ctr_number).encode(),
            self.acknowledge.encode(),
            self._usage_indicator.encode(),
            self._comp_sep.encode()
        ]

    def get_isa(self):
        isa = _ISA()
        isa.put_bytes_list(self.get_bytes_list_isa())
        return isa

    # build IEA
    def get_bytes_list_iea(self, groups : int):
        return [
            str(groups).encode(),
            str(self._ctr_number).encode()
        ]

    @property
    def control_num(self):
        return self._ctr_number

    def get_iea(self, groups : int):
        iea = _IEA()
        iea.put_bytes_list(self.get_bytes_list_iea(groups))
        return iea

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


def discover_template(st_se):
    type = int(st_se[0][1])
    out = None
    for template in template_operators.template_list:
        if template.identifier_code == type:
            temp = template.get_template()
            out = temp(st_se)
    return out


class EdiGroup(TemplateGroup):
    def __init__(self,isa:_ISA ,init_data=None, group_info=group_identifiers.Invoice(), partner_data=None):
        TemplateGroup.__init__(self)
        self.group_info = group_info
        self._GS = None
        self._GE = None
        self._ISA = isa
        self._partner_data = partner_data
        self._group_transaction = None
        #self._template_group = TemplateGroup()
        if init_data is not None:
            self._init_group_data = init_data
            self._init_process()
        elif self._partner_data and self.group_info:
            self._group_transaction = GroupTransaction(self._partner_data, self.group_info.identifier_code)
            self._GS = self._group_transaction.get_gs()

    def _init_process(self):
        # Discover gs/ge

        self._GS = _GS()
        self._GE = _GE()

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
                    out.set_isa_gs(self._ISA, self._GS)
                    self.append(out)
    def append(self, template: generic.Template):
        if self._partner_data:
            template.put_partnership(self._partner_data)
        template.set_isa_gs(self._ISA, self._GS)
        super().append(template)

    def get_content(self):
        return self

    @property
    def control_num(self):
        if self._group_transaction:
            return self._group_transaction.control_num
        return int(self._GS[6])

    def get_gs_ge(self):
        if self._group_transaction:
            self._GE = self._group_transaction.get_ge(self.__len__())
        return self._GS, self._GE


class EdiGroups(list):
    def append(self, edi_group : EdiGroup):
        super().append(edi_group)


class EdiHeader(list):
    def __init__(self, init_data=None, partner_data=None):
        list.__init__(self)
        self.ISA = None
        self.IEA = None
        #self._edi_groups = EdiGroups()

        self._ack_requested = False
        self.ack = None

        # For transactions with single message
        self._template = None

        self._partner_data = partner_data

        # Normal Init from opened edi file
        if init_data:
            self._init_edi_file = init_data
            self._init_process()
        elif partner_data:
            # Init for writing empty edi file, create ISA. IEA will be made at end
            self._edi_transaction = InterchangeTransaction(self._partner_data)
            self.ISA = self._edi_transaction.get_isa()

    def _init_process(self):
        # Discover isa/iea

        self.ISA = _ISA()
        self.IEA = _IEA()
        self._edi_transaction = None
        isa = None
        iea = None

        for section in self._init_edi_file:
            if clean_head(section[0]) == self.ISA.tag:
                isa = section
            elif clean_head(section[0]) == self.IEA.tag:
                iea = section

        if isa is not None:
            self.ISA.put_bytes_list(isa[1:])
        if iea is not None:
            self.IEA.put_bytes_list(iea[1:])

        # Discover if Ack Requested
        props = self.ISA.get_property_array()
        for prop in props:
            if prop.tag == 13:
                self._ack_requested = int(prop.content) == 1


        # discover all gs/ge Groups
        found_list = discover_all_sections(b'GS', b'GE', self._init_edi_file)

        # Check to see if no groups exist
        if found_list == []:
            found_list = discover_all_sections(b'ST', b'SE', self._init_edi_file)
            if found_list.__len__() == 1:
                self._template = discover_template(found_list[0])
                self._template.ISA = self.ISA
            # TODO: Raise some error that either no content exists or that content is not contained in group.
            else:
                pass
        else:
            for bytes_list in found_list:
                tmp = EdiGroup(self.ISA, bytes_list)
                self.append(tmp)

        # Ack
        if self._ack_requested:
            ack = acknowledgement.AckEdiEngine(self)
            self.ack = ack.get_ack()

    '''
    @param group: EdiGroup expected only
    '''
    def append(self, group: EdiGroup):
        super().append(group)

    # Appends group to appropriate group, creates new group in no appropriate group exists
    def append_template(self, template: generic.Template):
        tar_group = None
        for group in self:
            if group.group_info.identifier_code == template.group_info.identifier_code:
                tar_group = group
        if not tar_group:
            tar_group = EdiGroup(self.ISA, group_info=template.group_info, partner_data=self._partner_data)
            self.append(tar_group)
        tar_group.append(template)

    # Pass template and get tuple of template, group, and set id
    def get_id_tuple(self, template: generic.Template):
        tar_group = None
        for group in self:
            for content in group.get_content():
                if id(content) == id(template): tar_group = group
        return (self._edi_transaction.control_num,
                tar_group.control_num,
                template.control_num)

    # Returns all content in EDI file
    def get_all_content(self):
        content = TemplateGroup()
        if self._template:
            content.append(self._template)
            return content
        for group in self:
            content += group.get_content()
        return content

    # Get all bytes content from all content headers and groups
    def get_all_bytes_lists(self):
        if self._edi_transaction:
            self.IEA = self._edi_transaction.get_iea(self.__len__())

        # Method for single template form
        if self._template:
            return [self.ISA.get_bytes_list()] + self._template.get_bytes_list() + [self.IEA.get_bytes_list()]

        out_list = list()
        out_list.append(self.ISA.get_bytes_list())
        for group in self:
            gs,ge = group.get_gs_ge()
            out_list.append(gs.get_bytes_list())
            for content in group.get_content():
                out_list += content.get_bytes_list()
            out_list.append(ge.get_bytes_list())
        out_list.append(self.IEA.get_bytes_list())
        return out_list


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
        self.edi_header = EdiHeader()

    # Returns file in correctly formatted edi format
    def get_open_file(self):
        out_memory = io.BytesIO()
        for section in self.edi_header.get_all_bytes_lists():
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
            tmp_seperated = list()
            for sep in seperated:
                tmp_seperated.append(sep.strip())
            seperated_sections.append(tmp_seperated)
        self.edi_header = EdiHeader(seperated_sections)
