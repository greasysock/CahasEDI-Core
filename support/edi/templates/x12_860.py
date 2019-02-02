from . import generic
from .tags import _BCH, _REF, _PER, _DTM, _POC, _QTY, StatusValues

desc = "Purchase Order Change Request - Buyer Initiated"
i = 860

class Template(generic.Template):
    def __init__(self, start_data = None):

        structure = [
            (_BCH, StatusValues.Mandatory, 1, 0),
            (_REF, StatusValues.Optional, -1, 0),
            (_PER, StatusValues.Optional, 3, 1),
            (_DTM, StatusValues.Optional, 10, 1),
            [(_POC, StatusValues.Optional, -1 , 1),
                (_POC, StatusValues.Mandatory, 1, 1),
                [(_QTY, StatusValues.Optional, -1, 2),
                    (_QTY, StatusValues.Mandatory, 1, 2)]]
        ]

        generic.Template.__init__( self, i, desc, start_data=start_data, structure=structure)


class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()