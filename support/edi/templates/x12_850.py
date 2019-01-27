from . import generic
import io
from .tags import _BEG, _REF, _REF, _FOB, _CSH, _ITD, _DTM, _PWK, TD5, _TD4, _N1, _N3, _N4, _PER, _PO1, _CTP, _PID, _CTT


desc = "Purchase Order"
i = 850

class Template(generic.Template):
    def __init__(self, start_data = None):
        generic.Template.__init__(self, i, desc, start_data=start_data)


class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()