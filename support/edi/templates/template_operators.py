from support.edi.templates import generic

# Responsible for keeping track of installed templates


class Template_List(list):
    def append(self, obj : object):
        super().append(obj)


template_list = Template_List()
