import io
from .tags import _ST, _SE, _ISA, _GS, GENERIC_TAG, EmptyProperty, GenericProperty
from .template_operators import template_list, discover_all_sections, clean_head

# Generic template class operates as reader, writer, and validating class for all incoming and outdoing edi files.


class TemplateContentList(list):
    def append(self, obj : GENERIC_TAG):
        super().append(obj)


class Template:
    def __init__(self, template_id : int, template_description : str, start_data = None, structure = None):
        self._template_id = template_id
        self._template_description = template_description
        self._ST = _ST()
        self._SE = _SE()
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
            if clean_head(section[0]) == self._ST.tag:
                st = section
            elif clean_head(section[0]) == self._SE.tag:
                se = section

        if st is not None:
            self._ST.put_bytes_list(st[1:])
        if se is not None:
            self._SE.put_bytes_list(se[1:])

        if self._structure is not None:
            self._init_process_inner_data()

    def _init_process_inner_data(self):
        cursor = 1
        out_list = list()
        for structure in self._structure:


            cursor, tmp_list = self._unpack_data(structure, cursor)
            if tmp_list:
                if tmp_list.__len__() > 1:
                    tmp_list = [tmp_list,]
                out_list = out_list+tmp_list
        print(out_list)
        self._data = out_list

    def _unpack_data_depreciated(self, structure, cursor, in_list : list = None):
        if in_list is not None:
            out_list = in_list
        else:
            out_list = list()

        try:
            t = structure[0]().tag
            t_m = self._init_template_data[cursor][0].lstrip()
            print(t_m)

            if t != t_m:
                out_cursor = cursor
            elif t == t_m:
                print(cursor)
                out_cursor = cursor + 1
                data_tmp = structure[0]()
                target_tmp = self._init_template_data[cursor][1:]
                data_tmp.put_bytes_list(target_tmp)
                data_tmp.set_max(structure[2])
                data_tmp.set_min(structure[3])
                data_tmp.set_status(structure[1])
                out_list.append(data_tmp)
                print(out_cursor)
                print(self._init_template_data[out_cursor][0])

            # Start recursion search
            if self._init_template_data[out_cursor][0].lstrip() == structure[0]().tag:
                rep_list = list() + out_list
                finish = False
                while not finish:
                    out_cursor, out_list = self._unpack_data(structure, out_cursor,in_list=self._init_template_data)
                    rep_list.append(t)
                    if self._init_template_data[out_cursor][0] != structure[0]().tag:
                        finish = True
                out_list = list()
                out_list.append(rep_list)

        except TypeError:
            out_cursor, out_list = self._unpack_data(structure[0], cursor, out_list)
            if out_cursor != cursor:
                rec = structure[1:]

                tmp_list = list()
                tmp_list = tmp_list + out_list
                tmp_out_list = list()
                for s in rec[1:]:
                    if type(s) == list:
                        rec_list = list()
                        count = 0
                        for recursion in s:
                            out_cursor, rec_list_tmp = self._unpack_data(recursion, out_cursor)
                            if rec_list_tmp == []:
                                count += 1
                            else:
                                rec_list.append(rec_list_tmp)

                        if count != s.__len__():
                            tmp_list.append(rec_list)

                    elif type(s) == tuple:
                        out_cursor, tmp_list = self._unpack_data(s, out_cursor, tmp_list)

                tmp_out_list.append(tmp_list)
                out_list = tmp_out_list
                if self._init_template_data[out_cursor][0] == rec[0][0]().tag:

                    # Start recursion search
                    finish = False
                    while not finish:
                        tmp_list = list()
                        for s in rec:
                            out_cursor, tmp_list = self._unpack_data(s, out_cursor, tmp_list)
                        if self._init_template_data[out_cursor][0] != rec[0][0]().tag:
                            finish = True
                        out_list.append(tmp_list)
                t = list()
                t.append(out_list)
                out_list = t

        return out_cursor, out_list

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
        self._ISA = isa
        self._GS = gs

    def get_isa_gs(self):
        return (self._ISA, self._GS)

    def process_tag_to_dict(self, tag : GENERIC_TAG, max, min, importance):
        out_dict = dict()
        out_dict['occurrences'] = dict()
        out_dict['occurrences']['max'] = max
        out_dict['occurrences']['min'] = min
        out_dict['importance'] = importance.value.decode()
        out_dict['description'] = tag.content
        out_dict['tag'] = tag.tag.decode()
        out_dict['properties'] = dict()
        for k, prop in enumerate(tag.get_property_array()):
            if type(prop) == GenericProperty:

                prop_dict = dict()
                prop_dict['name'] = prop.name
                prop_dict['length'] = dict()
                prop_dict['length']['max'] = prop.max_length
                prop_dict['length']['min'] = prop.min_length
                prop_dict['importance'] = prop.status.value.decode()
                try:
                    prop_dict['content'] = prop.content.decode()
                except AttributeError:
                    prop_dict['content'] = prop.content
                out_dict['properties'][k] = prop_dict

            elif type(prop) == EmptyProperty:
                out_dict['properties'][k] = None
        return out_dict

    def get_detailed_content(self, input_content=None):
        if input_content:
            content = input_content
        else:
            content = self._data
        out_dict = dict()
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

    # Get detailed structure
    def get_detailed_structure(self, input_structure=None):

        if input_structure:
            out_ = dict()
            struct = input_structure
        else:
            out_ = dict()
            struct = self._structure
        if struct:
            if type(struct) == tuple:
                tag = struct[0]()
                return self.process_tag_to_dict(tag, struct[2], struct[3], struct[1])

            for i,structure in enumerate(struct):
                if type(structure) == tuple:
                    out_[i] = self.get_detailed_structure(input_structure=structure)
                elif type(structure) == list:
                    out_dict = dict()
                    for j,inner_structure in enumerate(structure):
                        out_dict[j] = self.get_detailed_structure(input_structure=inner_structure)
                    out_[i] = out_dict
            return out_
        return False

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
