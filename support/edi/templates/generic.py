import io
from .tags import _ST, _SE, GENERIC_TAG, EmptyProperty, GenericProperty
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
            # Check if tag matches current tag:
            cursor, tmp_list = self._unpack_data(structure, cursor)
            try:
                out_list = out_list+tmp_list
            except AttributeError:
                pass
            formatted = True

    def _unpack_data(self, structure, cursor, in_list : list = None):

        if in_list is not None:
            out_list = in_list
        else:
            out_list = list()

        try:
            t = structure[0]().tag
            t_m = self._init_template_data[cursor][0]

            if t != t_m:
                out_cursor = cursor
            elif t == t_m:
                out_cursor = cursor + 1
                data_tmp = structure[0]()
                target_tmp = self._init_template_data[cursor][1:]
                data_tmp.put_bytes_list(target_tmp)
                out_list.append(t)

            # Start recursion search
            if self._init_template_data[out_cursor][0] == structure[0]().tag:
                rep_list = list() + out_list
                finish = False
                while not finish:
                    out_cursor, out_list = self._unpack_data(structure, out_cursor)
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

    # Get
    def get_detailed_structure(self, input_structure=None):

        if input_structure:
            out_ = dict()
            struct = input_structure
        else:
            out_ = dict()
            struct = self._structure
        if struct:
            if type(struct) == tuple:
                out_dict = dict()
                out_dict['occurrences'] = dict()
                out_dict['occurrences']['max'] = struct[2]
                out_dict['occurrences']['min'] = struct[3]
                out_dict['importance'] = struct[1].value.decode()
                tag = struct[0]()
                out_dict['description'] = tag.content
                out_dict['tag'] = tag.tag.decode()
                out_dict['properties'] = dict()
                for k,prop in enumerate(tag.get_property_array()):
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
