from . import generic
import io
from .tags import _BEG, _REF, _REF, _FOB, _CSH, _ITD, _DTM, _PWK, _TD5, _TD4, _N1, _N3, _N4, _PER, _PO1, _CTP, _PID, _CTT, StatusValues


desc = "Purchase Order"
i = 850

class Template(generic.Template):
    def __init__(self, start_data = None):
        generic.Template.__init__(self, i, desc, start_data=start_data)

        structure = [
            (_BEG, StatusValues.Mandatory, 1, 1),
            (_REF, StatusValues.Optional, -1, 1),
            (_FOB, StatusValues.Optional, -1, 1),
            (_CSH, StatusValues.Optional, -1, 1),
            (_ITD, StatusValues.Optional, 5, 1),
            (_DTM, StatusValues.Optional, 10, 1),
            (_PWK, StatusValues.Optional, 25, 1),
            (_TD5, StatusValues.Optional, 12, 1),
            [(_N1, StatusValues.Optional, 200, 1),
                (_N1, StatusValues.Mandatory, 1, 1),
                    (_N3, StatusValues.Optional, 2, 2),
                    (_N4, StatusValues.Optional, -1, 2),
                    (_PER, StatusValues.Optional, -1, 2)],
            [(_PO1, StatusValues.Mandatory, 100000, 1),
                (_PO1, StatusValues.Mandatory, 1, 1),
                [(_CTP, StatusValues.Optional, -1, 2),
                    (_CTP, StatusValues.Mandatory, 1, 2)],
                [(_PID, StatusValues.Optional, 1000, 2),
                 (_PID, StatusValues.Mandatory, 1, 2)],
                (_PWK, StatusValues.Optional, 25, 2)
             ],
            [(_CTT, StatusValues.Optional, 1, 1),
             (_CTT, StatusValues.Mandatory, 1, 1)]
        ]

        generic.Template.__init__( self, i, desc, start_data=start_data, structure=structure)



class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()