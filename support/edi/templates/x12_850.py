from . import generic
import io


desc = "Purchase Order"
i = 850

class Template(generic.Template):
    def __init__(self, start_data = None):
        generic.Template.__init__(self, i, desc, start_data=start_data)


class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()