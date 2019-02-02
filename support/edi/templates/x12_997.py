from . import generic
from .tags import StatusValues, _AK1, _AK2, _AK3, _AK4, _AK5, _AK9

desc = "Functional Acknowledgment"
i = 997

class Template(generic.Template):
    def __init__(self, start_data=None):

        structure = [
            (_AK1, StatusValues.Mandatory, 1, 0),
            [(_AK2, StatusValues.Optional, 999999, 1),
                (_AK2, StatusValues.Optional, 1, 1),
                [(_AK3, StatusValues.Optional, 999999, 2),
                    (_AK3, StatusValues.Optional, 1, 2),
                    (_AK4, StatusValues.Optional, 99, 2)],
             (_AK5, StatusValues.Mandatory, 1, 1)],
            (_AK9, StatusValues.Mandatory, 1, 0)
        ]

        generic.Template.__init__( self, i, desc, start_data=start_data, structure=structure)



class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()