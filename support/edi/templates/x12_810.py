# Invoice
# Based on X12 004010 V1 Variant 10

from . import generic, template_operators
from .tags import _ISA, _IEA, _GS, _GE, _ST, _SE, _BIG, _REF, _N1, _N3, _N4, _ITD, _DTM, _FOB, _IT1, _PID, _SAC, _TXI, _TDS, _CAD, _AMT, _CTT, StatusValues, TagArray
import io

desc = "Invoice"
i = 810


class Template(generic.Template):
    def __init__(self, start_data = None):
        generic.Template.__init__( self, i, desc, start_data=start_data)

        # Structured in tuple with tag reference, followed by status, occurrences, and level
        # Example ( _BIG, StatusValues.Mandatory, 1, 0 )

        N1_N3_N4 = None

        self._810_structure = [
            (_BIG, StatusValues.Mandatory, 1, 0),
            (_REF, StatusValues.Optional, 12, 1),
            (_N1, StatusValues),
            _ITD,
            _DTM,
            _FOB,
            [_IT1, [_PID],[_SAC,_TXI]],
            _TDS,
            _CAD,
            _AMT,
            [_SAC,_TXI],
            _CTT
        ]


class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()
