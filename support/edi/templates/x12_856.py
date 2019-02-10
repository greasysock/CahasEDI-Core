from . import generic
from .tags import _BSN, _HL, _TD1, _TD5, _REF, _DTM, _N1, _N3, _N4, _PRF, _MAN, _LIN, _SN1, _PID, _CTT, StatusValues
from .. import group_identifiers

desc = "Ship Notice/Manifest"
i = 856

class Template(generic.Template):
    def __init__(self,start_data = None):

        structure = [
            (_BSN, StatusValues.Mandatory, 1, 0),
            [(_HL, StatusValues.Mandatory, 2000000, 1),
                (_HL, StatusValues.Mandatory, 1, 1),
                (_TD1, StatusValues.Optional, 20, 2),
                (_TD5, StatusValues.Mandatory, 12, 2),
                (_REF, StatusValues.Mandatory, -1, 2),
                (_DTM, StatusValues.Mandatory, 10, 2),
                [ (_N1, StatusValues.Mandatory, 200, 2),
                    (_N1, StatusValues.Mandatory, 1, 2),
                    (_N3, StatusValues.Optional, 2, 3),
                    (_N4, StatusValues.Optional, 1, 3)]],
            [(_HL, StatusValues.Mandatory, 200000, 1),
                (_HL, StatusValues.Mandatory, 1, 1),
                (_PRF, StatusValues.Mandatory, 1, 2),
                (_TD1, StatusValues.Optional, 20, 2)],
            [(_HL, StatusValues.Mandatory, 200000, 1),
             (_HL, StatusValues.Mandatory, 1, 1),
             (_MAN, StatusValues.Optional, -1, 2)],
            [(_HL, StatusValues.Mandatory, 200000, 1),
                (_HL, StatusValues.Mandatory, 1, 1),
                (_LIN, StatusValues.Mandatory, 1, 2),
                (_SN1, StatusValues.Mandatory, 1, 2),
                (_PID, StatusValues.Mandatory, 200, 2)],
            (_CTT, StatusValues.Optional, 1, 0)
            ]

        generic.Template.__init__( self, i, desc, start_data=start_data, structure=structure, group_info=group_identifiers.ShipNotice)


class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()