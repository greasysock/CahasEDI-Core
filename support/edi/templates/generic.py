import io
from .tags import _ISA, _IEA, _GS, _GE, _ST, _SE
from .template_operators import template_list, discover_all_sections, clean_head

# Generic template class operates as reader, writer, and validating class for all incoming and outdoing edi files.


class Template:
    def __init__(self, template_id : int, template_description : str, start_data = None):
        self._template_id = template_id
        self._template_description = template_description
        self._ST = _ST()
        self._SE = _SE()

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
