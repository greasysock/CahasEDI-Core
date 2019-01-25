import io
from .tags import _ST, _SE, GENERIC_TAG
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
            out_list = out_list + tmp_list
            formatted = True
            print("")

    def _unpack_data(self, structure, cursor, in_list : list = None):

        if in_list is not None:
            out_list = in_list
        else:
            out_list = list()

        try:
            t = structure[0]().tag
            t_m = self._init_template_data[cursor][0]

            print(t)
            print(t_m)

            if t != t_m:
                out_cursor = cursor
            elif t == t_m:
                out_cursor = cursor + 1
                out_list.append(t)

                print("match")
            # Start recursion search
            if self._init_template_data[out_cursor][0] == structure[0]().tag:
                print("rep found")
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
            out_cursor, out_list = self._unpack_data(structure[0], cursor)
            if out_cursor != cursor:
                print("rec found")
                rec = structure[1:]

                tmp_list = list()
                tmp_list = tmp_list + out_list
                tmp_out_list = list()
                for s in rec[1:]:
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
        print(out_cursor)
        print(out_list)
        return out_cursor, out_list

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
