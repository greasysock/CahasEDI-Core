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

    # We need to find the invoice id and assign that to content id and the purchase order id and assign them to parent ids
    def _init_process(self):
        super()._init_process()

        # Invoice ID
        self._content_id = self._mapped_data[0][2].decode()

        # Purchase Order Number
        self._content_parent_ids.append(self._mapped_data[0][4].decode())
    
    # Get invoice information, line items, totals, addresses etc.
    def get_custom_detailed_content(self):
        def get_item_date(item):
            out = dict()
            out['date'] = item[2].decode()
            out['type'] = item[1].decode()
            return out
        def get_address(item):
            def get_street(item):
                return item[1].decode()
            def get_geographic(item):
                out = dict()
                out['city'] = item[1].decode()
                out['state']  = item[2].decode()
                out['zip code'] = item[3].decode()
                out['country'] = item[4].decode()
                return out
            out = dict()
            out['type'] = item[0][1].decode()
            out['name'] = item[0][2].decode()
            out['street address'] = list()
            if item.__len__() >= 2 and type(item[1]) == _N3:
                out['street address'].append(get_street(item[1]))
            elif item.__len__() >= 2 and type(item[1]) == _N4:
                geo = get_geographic(item[1])
                out.update(geo)
            if item.__len__() >= 3 and type(item[2]) == _N4:
                geo = get_geographic(item[2])
                out.update(geo)
            return out
        def get_terms(item):
            out = {
                'type' : None,
                'discount' : list(),
                'net days' : None,
                'description' : None
            }
            if item[1]:
                out['type'] = item[1].decode()
            if item[3]:
                out['discount'] = dict()
                out['discount']['percent'] = item[3].decode()
                out['discount']['days due'] = item[5].decode()
            if item[7]:
                out['net days'] = item[7].decode()
            if item[12]:
                out['description'] = item[12].decode()
            return out
        def get_line_item(item):
            out = dict()
            return out
        out_dict = dict()

        out_dict['date'] = self._mapped_data[0][1].decode()
        out_dict['purchase order date'] = self._mapped_data[0][1].decode()

        # Creating addresses
        out_dict['addresses'] = list()
        if type(self._mapped_data[2][0]) ==  list:
            for address_details in self._mapped_data[2]:
                out_dict['addresses'].append(get_address(address_details))
        else:
            out_dict['addresses'].append(get_address(self._mapped_data[2]))
        
        # Creating terms
        out_dict['terms'] = list()
        if type(self._mapped_data[3]) == list:
            pass
        elif type(self._mapped_data[3]) == _ITD:
            out_dict['terms'].append(get_terms(self._mapped_data[3]))

        # Handling DTM section
        out_dict['item dates'] = list()
        if type(self._mapped_data[4]) == list:
            pass
        else:
            out_dict['item dates'].append(get_item_date(self._mapped_data[4]))
        
        # Getting line items
        out_dict['line items'] = list()
        if self._mapped_data[6] and type(self._mapped_data[6][0]) == list:
            for line_item in self._mapped_data[6]:
                out_dict['line items'].append(get_line_item(line_item))
        elif self._mapped_data[6] and type(self._mapped_data[6][0]) == _IT1:
            out_dict['line items'].append(get_line_item(self._mapped_data[6]))
        return out_dict


class TemplateDescription(generic.TemplateDescription):
    def __init__(self):
        generic.TemplateDescription.__init__(self, i, desc, Template)


description = TemplateDescription()
