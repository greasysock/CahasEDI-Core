import io
from .template_operators import template_list

# Generic template class operates as reader, writer, and validating class for all incoming and outdoing edi files.

class Template:
    def __init__(self, edi_file : io.BytesIO, template_id : int, template_description : str, separator = b'*', terminator = b'~', sub_separator = b'>', repeating = b'^'):
        self._separator = separator
        self._terminator = terminator
        self._sub_separator = sub_separator
        self._repeating = repeating

        self._template_id = template_id
        self._template_description = template_description
        self._edi_file = edi_file
        self._to_bytes_array()

    def _to_bytes_array(self):
        lines = self._edi_file.readlines()

        out_bytes = b''
        for line in lines:
            line = line.rstrip(b'\n')
            out_bytes += line

        edi_dict = dict()
        out_bytes_sections = out_bytes.split(self._terminator)

        for section in out_bytes_sections:
            print(section.split(self._separator))

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
