from . import generic
from .tags import _BAK, _CUR, _REF, _CSH, _PO1, _PID, _ACK, _CTT, StatusValues
from .. import group_identifiers

desc = "Purchase Order Acknowledgment"
i = 855

class Template(generic.Template):
    def __init__(self, start_data = None):

        structure = [
            (_BAK, StatusValues.Mandatory, 1, 0),
            (_CUR, StatusValues.Optional, 1, 0),
            (_REF, StatusValues.Mandatory, -1, 1),
            (_CSH, StatusValues.Optional, 1, 0),
            [(_PO1, StatusValues.Optional, 100000, 1),
                (_PO1, StatusValues.Mandatory, 1, 1),
                [(_PID, StatusValues.Optional, 1000, 2),
                    (_PID, StatusValues.Mandatory, 1, 2)],
                [(_ACK, StatusValues.Mandatory, 104, 2),
                    (_ACK, StatusValues.Mandatory, 1, 2)]],
            [(_CTT, StatusValues.Optional, 1, 1),
                (_CTT, StatusValues.Optional, 1, 1)]
        ]

        generic.Template.__init__( self, i, desc, start_data=start_data, structure=structure, group_info=group_identifiers.PurchaseOrderAcknowledgement)



class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()