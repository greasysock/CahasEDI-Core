import io
from .tags import _ST, _SE, _ISA, _GS, GENERIC_TAG, EmptyProperty, GenericProperty
from .template_operators import template_list, discover_all_sections, clean_head
from .. import group_identifiers
# Generic template class operates as reader, writer, and validating class for all incoming and outdoing edi files.


class TemplateContentList(list):
    def append(self, obj : GENERIC_TAG):
        super().append(obj)


class Template:
    def __init__(self, template_id : int, template_description : str, start_data = None, structure = None, group_info = None):
        self._template_id = template_id
        self._template_description = template_description
        self.ST = _ST()
        self.SE = _SE()
        self.GS = None
        self.ISA = None
        self._control_num = None
        self._partnership_data = None
        self._content_id = None
        self._content_parent_ids = list()
        self.group_info = group_identifiers.Invoice()
        if group_info:
            self.group_info = group_info()
        self._template_content = TemplateContentList()

        self._structure = structure
        self._data = None
        if start_data is not None:
            self._init_template_data = start_data
            self._init_process()

    def _init_process(self):
        st = None
        se = None

        for section in self._init_template_data:
            if clean_head(section[0]) == self.ST.tag:
                st = section
            elif clean_head(section[0]) == self.SE.tag:
                se = section

        if st is not None:
            self.ST.put_bytes_list(st[1:])
            self._control_num = int(self.ST[2])
        else:
            # If no ST/SE exists, fill with empty values to be filled later.
            st = [self.ST.tag, b'', b'']
            self._init_template_data = [st] + self._init_template_data
            self.ST.put_bytes_list(st[1:])
        if se is not None:
            self.SE.put_bytes_list(se[1:])
        else:
            se = [self.SE.tag, b'', b'']
            self._init_template_data = self._init_template_data + [se]
            self.SE.put_bytes_list(se[1:])
        if self._structure is not None:
            self._init_process_inner_data()

    def _init_process_inner_data(self):
        cursor = 1
        out_list = list()
        out_order = list()
        for structure in self._structure:
            cursor, tmp_list = self._unpack_data(structure, cursor)
            if tmp_list:
                if tmp_list.__len__() > 1:
                    tmp_list = [tmp_list,]
                out_list = out_list+tmp_list
                out_order = out_order+tmp_list
            else:
                out_order.append(None)
        self._mapped_data = out_order
        self._data = out_list

    def _prepare_tag(self, tag, cursor, min, max, status):
        tag_data = tag()
        target_data = self._init_template_data[cursor][1:]

        tag_data.put_bytes_list(target_data)
        tag_data.set_max(max)
        tag_data.set_min(min)
        tag_data.set_status(status)

        return tag_data

    # Maps data to template format
    def _unpack_data(self, structure, cursor: int, in_list=None):
        out_list = list()

        # Check for list for recursion methods
        if in_list:
            out_list = in_list

        # Recursion when structure is it's most simple
        if type(structure) == tuple and structure[0]().tag == self._init_template_data[cursor][0]:
            out_list.append(self._prepare_tag(structure[0],cursor, structure[3], structure[2], structure[1]))
            cursor += 1

            # Check for extra elements, but only if supported.
            if (structure[2] > 1 or structure[2] == -1) and structure[0]().tag == self._init_template_data[cursor][0]:
                cursor, out_list = self._unpack_data(structure, cursor, out_list)

        # Branching recursion
        elif type(structure) == list:
            # Branch head using iteration
            branch_head = structure[0]
            while branch_head[0]().tag == self._init_template_data[cursor][0]:

                # tmp branch list is used to help keep data on correct level
                tmp_branch_list = list()
                for strut in structure[1:]:
                    cursor, tmp_branch_list = self._unpack_data(strut, cursor, tmp_branch_list)
                out_list = out_list + [tmp_branch_list]


        return cursor, out_list

    def set_isa_gs(self, isa: _ISA, gs: _GS):
        self.ISA = isa
        self.GS = gs

    def get_isa_gs(self):
        return (self.ISA, self.GS)

    def process_tag_to_dict(self, tag : GENERIC_TAG, max, min, importance):
        out_dict = dict()
        out_dict['occurrences'] = dict()
        out_dict['occurrences']['max'] = max
        out_dict['occurrences']['min'] = min
        out_dict['importance'] = importance.value.decode()
        out_dict['description'] = tag.content
        out_dict['tag'] = tag.tag.decode()
        out_dict['properties'] = list()
        for k, prop in enumerate(tag.get_property_array()):
            if type(prop) == GenericProperty:

                prop_dict = dict()
                prop_dict['name'] = prop.name
                prop_dict['id'] = prop.tag
                prop_dict['length'] = dict()
                prop_dict['length']['max'] = prop.max_length
                prop_dict['length']['min'] = prop.min_length
                prop_dict['importance'] = prop.status.value.decode()
                try:
                    prop_dict['content'] = prop.content.decode()
                except AttributeError:
                    prop_dict['content'] = prop.content
                out_dict['properties'].append(prop_dict)

            elif type(prop) == EmptyProperty:
                out_dict['properties'].append(None)
        return out_dict

    def get_detailed_content(self, input_content=None):
        if input_content:
            content = input_content
        else:
            content = self._data
        out_list = list()
        if content:
            if type(content) != list:
                return self.process_tag_to_dict(content, content.max, content.min, content.status)
            for i, cont in enumerate(content):
                if type(cont) != list:
                    out_list.append(self.get_detailed_content(input_content=cont))
                elif type(cont) == list:
                    tmp_list = list()
                    for j,inner_cont in enumerate(cont):
                        tmp_list.append(self.get_detailed_content(input_content=inner_cont))
                    out_list.append(tmp_list)
            return out_list
        return False

    def get_detailed_content_old(self, input_content=None):
        if input_content:
            content = input_content
        else:
            content = self._data
        out_dict = dict()
        out_list = list()
        if content:
            if type(content) != list:
                return self.process_tag_to_dict(content, content.max, content.min, content.status)
            for i, cont in enumerate(content):
                if type(cont) != list:
                    out_dict[i] = self.get_detailed_content(input_content=cont)
                elif type(cont) == list:
                    tmp_dict = dict()
                    for j,inner_cont in enumerate(cont):
                        tmp_dict[j] = self.get_detailed_content(input_content=inner_cont)
                    out_dict[i] = tmp_dict
            return out_dict
        return False

    # Returns list of list of bytes of content. Requires recursion, based off get_detailed_structure
    def get_bytes_list(self, input_content=None):
        if input_content:
            content = input_content
        else:
            content = self._data
        out_list = list()
        if content:
            if type(content) != list:
                return content.get_bytes_list()
            for section in content:
                if type(section) != list:
                    out_list.append(self.get_bytes_list(input_content=section))
                elif type(section) == list:
                    for inner_section in section:
                        tmp_out = self.get_bytes_list(inner_section)
                        if type(tmp_out[0]) != list:
                            tmp_out = [tmp_out]
                        out_list += tmp_out
            if content == self._data:
                out_list = [self.ST.get_bytes_list()] + out_list + [self.SE.get_bytes_list()]
            return out_list

        return False

    # Get detailed structure
    def get_detailed_structure(self, input_structure=None):
        out_ = list()
        if input_structure:
            struct = input_structure
        else:
            struct = self._structure
        if struct:
            if type(struct) == tuple:
                tag = struct[0]()
                return self.process_tag_to_dict(tag, struct[2], struct[3], struct[1])

            for i,structure in enumerate(struct):
                if type(structure) == tuple:
                    out_.append(self.get_detailed_structure(input_structure=structure))
                elif type(structure) == list:
                    out_list = list()
                    for j,inner_structure in enumerate(structure):
                        out_list.append(self.get_detailed_structure(input_structure=inner_structure))
                    out_.append(out_list)
            return out_
        return False

    def get_segment_count(self):
        return self.get_bytes_list().__len__()

    # Assign a partner and generate ST/SE
    def put_partnership(self, partnership_data):
        self._partnership_data = partnership_data
        self._control_num = self._partnership_data.set_counter
        st = [str(self.template_type).encode(), str(self._control_num).encode()]
        se = [str(self.get_segment_count()).encode(), str(self._control_num).encode()]

        self.ST = _ST()
        self.ST.put_bytes_list(st)
        self.SE = _SE()
        self.SE.put_bytes_list(se)

    # TODO:
    def put_detailed_structure(self, detailed_structure):
        pass

    # Unique id for content type, including purchase order number/invoice number
    @property
    def content_id(self):
        return self._content_id

    # Unique id for content parent, including order number for a purchase order change etc.
    @property
    def content_parent_ids(self):
        return self._content_parent_ids

    @property
    def control_num(self):
        return self._control_num

    @property
    def template_type(self):
        return self._template_id

    def __str__(self):
        return "| {} Template - \"{}\" |".format(self._template_id, self._template_description)


class TemplateDescription:
    def __init__(self, template_id : int, template_description : str, template : object):
        self._id = template_id
        self._description = template_description
        self._template = template
        template_list.append(self)

    @property
    def identifier_code(self):
        return self._id

    @property
    def description(self):
        return self._description

    def get_template(self):
        return self._template
