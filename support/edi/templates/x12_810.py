# Invoice
# Based on X12 004010 V1 Variant 10

from . import generic, template_operators
from .tags import _BIG, _REF, _N1, _N3, _N4, _ITD, _DTM, _FOB, _IT1, _PID, _SAC, _TXI, _TDS, _CAD, _AMT, _CTT, StatusValues
from .. import group_identifiers

desc = "Invoice"
i = 810


class Template(generic.Template):
    def __init__(self, start_data = None):
        # Structured in tuple with tag reference, followed by status, occurrences, and level
        # Example ( _BIG, StatusValues.Mandatory, 1, 0 ), if occ -1, occ = >1

        structure = [
            (_BIG, StatusValues.Mandatory, 1, 0),
            (_REF, StatusValues.Optional, 12, 1),
            [(_N1, StatusValues.Optional, 200, 1),
                (_N1, StatusValues.Mandatory, 1, 1),
                (_N3, StatusValues.Optional, 2, 2),
                (_N4, StatusValues.Optional, 1, 2)],
            (_ITD, StatusValues.Mandatory, -1, 1),
            (_DTM, StatusValues.Mandatory,10,1),
            (_FOB, StatusValues.Optional, 1, 0),
            [(_IT1, StatusValues.Mandatory, 200000, 1),
                (_IT1, StatusValues.Mandatory, 1, 1),
                [(_PID, StatusValues.Optional, 1000, 2),
                    (_PID, StatusValues.Mandatory, 1, 2)],
                [(_SAC, StatusValues.Optional, 25, 2),
                    (_SAC, StatusValues.Mandatory, 1, 2),
                    (_TXI, StatusValues.Optional, 20,3)]],
            (_TDS, StatusValues.Mandatory, 1, 0 ),
            (_CAD, StatusValues.Mandatory, 1, 0),
            (_AMT, StatusValues.Optional, -1, 1),
            [(_SAC, StatusValues.Optional, 25, 1),
                (_SAC, StatusValues.Mandatory, 1, 1),
                (_TXI, StatusValues.Optional, 10, 2)],
            (_CTT, StatusValues.Optional, 1, 0)
        ]

        generic.Template.__init__( self, i, desc, start_data=start_data, structure=structure, group_info=group_identifiers.Invoice)

    def _init_process(self):
        super()._init_process()
        

class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()
