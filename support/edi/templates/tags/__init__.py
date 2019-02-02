from enum import Enum

# Classes and methods that control, verify, and read incoming and outgoing edi files.


def get_tags():
    t = ISA.get_tags()
    return t


class StatusValues(Enum):
    Mandatory = b'M'
    Required = b'R'
    Conditional = b'C'
    Optional = b'O'
    Floating = b'F'
    Dependent = b'D'
    Advised = b'A'
    Situational = b'S'
    NotUsed = b'X'
    NotRecommended = b'N'


class GenericProperty:
    def __init__(self, min_length : int, max_length : int, name, status : StatusValues, tag : int, value_type = None):
        self._min_length = min_length
        self._max_length = max_length
        self._name = name
        self._status = status
        self._tag = tag

        self._content = None

    @property
    def min_length(self):
        return self._min_length

    @property
    def max_length(self):
        return self._max_length

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        return self._status

    @property
    def content(self):
        return self._content

    def set_content(self, content):

        if self._content is None:
            self._content = content

    def __str__(self):
        return " [ {}: \"{}\" ] ".format(self._name, self._content.decode("utf-8"))


class EmptyProperty:
    pass


class GENERIC_TAG:
    _tags = list()
    def __init__(self, tag, content, status = StatusValues.Mandatory , max_occ = 1, level = 0):
        self._counter = None
        self._no = None
        self._tag = tag
        self._status = status
        self._max_occ = max_occ
        self._min_occ = 1
        self._level = level
        self._content = content
        self._property_array = list()

    def set_status(self, status: StatusValues):
        self._status = status

    def set_max(self, max: int):
        self._max_occ = max

    def set_min(self, min: int):
        self._min_occ = min

    def _append_tag(self, tag_obj):
        self._tags.append(tag_obj)

    @property
    def status(self):
        return self._status

    @property
    def max(self):
        return self._max_occ

    @property
    def min(self):
        return self._min_occ

    @property
    def level(self):
        return self._level

    @property
    def tag(self):
        return self._tag

    @property
    def content(self):
        return self._content

    def get_tags(self):
        return self._tags

    def get_property_array(self):
        return self._property_array

    def put_bytes_list(self, bytes_list : list):
#        print(self.content)
#        print(self.content)
        for i,value in enumerate(bytes_list):
            if type(self._property_array[i]) == GenericProperty:
                self._property_array[i].set_content(value.strip())
#                print(self._property_array[i])


# Tag list for layered tags

class TagArray:
    def __init__(self, max_occ : int, level : int, status : StatusValues, *argv : GENERIC_TAG or object):
        self._array = list()
        self._max_occ = max_occ
        self._level = level
        self._status = status

        for arg in argv:
            self._array.append(arg)
        pass


class _ISA(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'ISA', "Interchange Control Header")

        self._property_array = [
            GenericProperty(2, 2, "Authorization Information Qualifier", StatusValues.Mandatory, 1),
            GenericProperty(10,10, "Authorization Information", StatusValues.Mandatory, 2),
            GenericProperty(2, 2, "Security Information Qualifier", StatusValues.Mandatory, 3),
            GenericProperty(10, 10, "Security Information", StatusValues.Mandatory, 4),
            GenericProperty(2, 2, "Interchange ID Qualifier", StatusValues.Mandatory, 5),
            GenericProperty(15, 15, "Interchange Sender ID", StatusValues.Mandatory, 6),
            GenericProperty(2, 2, "Interchange ID Qualifier", StatusValues.Mandatory, 5),
            GenericProperty(15, 15, "Interchange Receiver ID", StatusValues.Mandatory, 7),
            GenericProperty(6, 6, "Interchange Date", StatusValues.Mandatory, 8),
            GenericProperty(4, 4, "Interchange Time", StatusValues.Mandatory, 9),
            GenericProperty(1, 1, "Interchange Control Standards Identifier", StatusValues.Mandatory, 10),
            GenericProperty(5, 5, "Interchange Control Version Number", StatusValues.Mandatory, 11),
            GenericProperty(9, 9, "Interchange Control Number", StatusValues.Mandatory, 12),
            GenericProperty(1, 1, "Acknowledgment Requested", StatusValues.Mandatory, 13),
            GenericProperty(1, 1, "Usage Indicator", StatusValues.Mandatory, 14),
            GenericProperty(1, 1, "Component Element Separator", StatusValues.Mandatory, 15),
        ]

        self._append_tag(self)


ISA = _ISA()


class _GS(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'GS', "Functional Group Header")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2, 2, "Functional Identifier Code", StatusValues.Mandatory, 479),
            GenericProperty(2, 15, "Application Sender's Code", StatusValues.Mandatory, 142),
            GenericProperty(2, 15, "Application Receiver's Code", StatusValues.Mandatory, 124),
            GenericProperty(8, 8, "Date", StatusValues.Mandatory, 373),
            GenericProperty(4, 8, "Time", StatusValues.Mandatory, 337),
            GenericProperty(1, 9, "Group Control Number", StatusValues.Mandatory, 28),
            GenericProperty(1, 2, "Responsible Agency Code", StatusValues.Mandatory, 455),
            GenericProperty(1, 12, "Version / Release/ Industry / Identifier Code", StatusValues.Mandatory, 480)
        ]


GS = _GS()


class _ST(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'ST', "Transaction Set Header")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(3, 3, "Transaction Set Identifier COde", StatusValues.Mandatory, 143),
            GenericProperty(2, 15, "Transaction Set Control Number", StatusValues.Mandatory, 329)
        ]


ST = _ST()


class _BIG(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'BIG', "Beginning Segment for Invoice")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(8, 8, "Date", StatusValues.Mandatory, 373),
            GenericProperty(1, 22, "Transaction Set Control Number", StatusValues.Mandatory, 76),
            GenericProperty(8, 8, "Date", StatusValues.Optional, 373),
            GenericProperty(10, 10, "Transaction Set Control Number", StatusValues.Optional, 324)
        ]


BIG = _BIG()


class _REF(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'REF', "Reference Identification")
        self._append_tag(self)
        self._property_array = [
            GenericProperty(2, 3, "Reference Identification Qualifier", StatusValues.Mandatory, 128),
            GenericProperty(1, 30, "Reference Identification", StatusValues.Conditional, 127),
            GenericProperty(1, 80, "Description", StatusValues.Optional, 352)
        ]


REF = _REF()


class _N1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'N1', "Name")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,3, "Entity Identifier Code", StatusValues.Mandatory, 98),
            GenericProperty(1,60, "Name", StatusValues.Conditional, 93),
            GenericProperty(1,2, "Identification Code Qualifier", StatusValues.Conditional, 66),
            GenericProperty(2,80, "Identification Code", StatusValues.Conditional, 67)
        ]


N1 = _N1()


class _N3(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'N3', "Address Information")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1, 55, "Address Information", StatusValues.Mandatory, 166),
        ]


N3 = _N3()


class _N4(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'N4', "Geographic Location")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2, 30, "City Name", StatusValues.Optional, 19),
            GenericProperty(2, 2, "State or Province Code", StatusValues.Optional, 156),
            GenericProperty(3, 15, "Postal Code", StatusValues.Optional, 116),
            GenericProperty(2, 3, "Country Code", StatusValues.Optional, 26),

        ]


N4 = _N4()


class _ITD(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'ITD', "Terms of Sale/Deterred Terms of Sale")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2, 2, "Terms Type Code", StatusValues.Optional, 336),
            EmptyProperty(),
            GenericProperty(1,6,"Terms Discount Percent", StatusValues.Optional, 338),
            EmptyProperty(),
            GenericProperty(1,3, "Terms Discount Days Due", StatusValues.Conditional, 351),
            EmptyProperty(),
            GenericProperty(1,3, "Terms Net Days", StatusValues.Optional, 386),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(1, 80, "Description", StatusValues.Optional, 352)

        ]



ITD = _ITD()


class _DTM(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'DTM', "Date/Time Reference")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(3, 3, "Date/Time Qualifier", StatusValues.Mandatory, 374),
            GenericProperty(8, 8, "Date", StatusValues.Conditional, 373),

        ]


DTM = _DTM()


class _FOB(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'FOB', "F.O.B. Related Instructions")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2, 2, "Shipment Method of Payment", StatusValues.Mandatory, 146),
        ]


FOB = _FOB()


class _IT1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'IT1', "Baseline Item Data (Invoice)")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1, 20, "Assigned Identification", StatusValues.Optional, 350),
            GenericProperty(1, 20, "Quantity Invoiced", StatusValues.Conditional, 358),
            GenericProperty(2, 2, "Unit or Basis for Measurement", StatusValues.Conditional, 355),
            GenericProperty(1, 17, "Unit Price", StatusValues.Conditional, 212),
            GenericProperty(2, 2, "Basis of Unit Price Code", StatusValues.Optional, 639),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Mandatory, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Mandatory, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Mandatory, 234),
        ]


IT1 = _IT1()


class _PID(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'PID', "Product/Item Description")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1, 1, "Item Description Type", StatusValues.Mandatory, 349),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(1, 80, "Description", StatusValues.Conditional, 352),
        ]


PID = _PID()


class _SAC(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'SAC', "Sevice, Promotion, Allowance, or Charge Information")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1, 1, "Allowance or Charge Indicator", StatusValues.Mandatory, 248),
            GenericProperty(4, 4, "Service, Promotion, Allowance, or Charge Code", StatusValues.Conditional, 1300),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(1, 15, "Amount", StatusValues.Optional, 610),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(2, 2, "Allowance or Charge Method of Handling Code", StatusValues.Optional, 331),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(1, 80, "Description", StatusValues.Conditional, 352)
        ]


SAC = _SAC()


class _TXI(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'TXI', "Tax Information")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2,"Tax Type Code",StatusValues.Mandatory,963),
            GenericProperty(1,18,"Monetary Amount" , StatusValues.Conditional,782),
            GenericProperty(1,10,"Percent" , StatusValues.Conditional,954),
            GenericProperty(2,2,"Tax Jurisdiction Code Qualifier" , StatusValues.Conditional,955),
            GenericProperty(1, 10, "Tax Jurisdiction Code", StatusValues.Conditional,956),
            GenericProperty(1,1,"Tax Exempt Code" , StatusValues.Conditional,441),
            GenericProperty(1,1,"Relationship Code" , StatusValues.Optional,662),
            GenericProperty(1,9,"Dollar Basis For Percent" , StatusValues.Optional,828),
            GenericProperty(1,20, "Tax Identification Number", StatusValues.Optional,325),
            GenericProperty(1,20, "Assigned Identification", StatusValues.Optional,350),
        ]


TXI = _TXI()


class _TDS(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'TDS', "Total Monetary Value Summary")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1, 15, "Amount", StatusValues.Mandatory, 610),
        ]


TDS = _TDS()


class _CAD(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'CAD', "Carrier Detail")
        self._append_tag(self)


        self._property_array = [
            GenericProperty(1, 2, "Transportation Method/Type Code", StatusValues.Mandatory, 91),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(2, 4, "Standard Carrier Alpha Code", StatusValues.Mandatory, 140),
            GenericProperty(1, 35, "Routing", StatusValues.Mandatory, 387),
            EmptyProperty(),
            GenericProperty(2, 3, "Reference Identification Qualifier", StatusValues.Mandatory, 128),
            GenericProperty(1, 30, "Reference Identification", StatusValues.Mandatory, 127),
        ]


CAD = _CAD()


class _AMT(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'AMT', "Monetary Amount")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1, 18, "Amount Qualifier Code", StatusValues.Mandatory, 522),
            GenericProperty(1,18, "Monetary Amount", StatusValues.Mandatory, 782)
        ]


AMT = _AMT()


class _CTT(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'CTT', "Transaction Totals")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1, 6, "Number of Line Items", StatusValues.Mandatory, 354),
            GenericProperty(1, 10, "Hash Total", StatusValues.Optional, 347),
            GenericProperty(1, 10, "Weight", StatusValues.Conditional, 81),
            GenericProperty(2,2, "Unit or Basis for Measurement Code", StatusValues.Conditional, 355),
            GenericProperty(1, 8, "Volume", StatusValues.Conditional, 183),
            GenericProperty(2,2, "Unit or Basis for Measurement Code", StatusValues.Conditional, 355),
            GenericProperty(1,80, "Description", StatusValues.Optional, 352)
        ]


CTT = _CTT()


class _SE(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'SE', "Transaction Set Trailer")
        self._append_tag(self)
        self._property_array = [
            GenericProperty(1, 10, "Number of Included Segments", StatusValues.Mandatory, 96),
            GenericProperty(4, 9, "Transaction Set Control Number", StatusValues.Mandatory, 329),
        ]


SE = _SE()


class _GE(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'GE', "Transaction Group Trailer")
        self._append_tag(self)
        self._property_array = [
            GenericProperty(1, 6, "Number of Transaction Sets Included", StatusValues.Mandatory, 97),
            GenericProperty(1, 9, "Group Control Number", StatusValues.Mandatory, 28),
        ]


GE = _GE()


class _IEA(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'IEA', "Interchange Control Trailer")
        self._append_tag(self)
        self._property_array = [
            GenericProperty(1, 5, "Number of Included Functional Groups", StatusValues.Mandatory, 16),
            GenericProperty(9, 9, "Interchange Control Number", StatusValues.Mandatory, 12)
        ]


IEA = _IEA()


class _BIA(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'BIA', "Beginning Segment for Inventory Inquiry/Advice")
        self._append_tag(self)


BIA = _BIA()

class _BEG(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'BEG', "Beginning Segment for Purchase Order")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2, "Transaction Set Purpose Code", StatusValues.Mandatory, 353),
            GenericProperty(2,2, "Purchase Order Type Code", StatusValues.Mandatory, 92),
            GenericProperty(10,10, "Purchase Order Number", StatusValues.Mandatory, 324),
            EmptyProperty(),
            GenericProperty(8,8,"Date", StatusValues.Mandatory, 373)
        ]


BEG = _BEG()

class _LIN(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'LIN', "Item Identification")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,20,"Assigned Identification", StatusValues.Optional,350),
            GenericProperty(2,2,"Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1,48, "Product/Service ID", StatusValues.Mandatory, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Mandatory, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Mandatory, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Mandatory, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Mandatory, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Mandatory, 234),
        ]


LIN = _LIN()


class _QTY(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'QTY', "Quantity Available")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2,"Quantity Qualifier", StatusValues.Mandatory, 673),
            GenericProperty(1,15,"Quantity", StatusValues.Conditional, 380),
            GenericProperty(2,2,"Unit or Basis for Measurement Code", StatusValues.Mandatory, 355)
        ]


QTY = _QTY()


class _SCH(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'SCH', "Line Item Schedule")
        self._append_tag(self)


SCH = _SCH()


class _CSH(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'CSH', "Sales Requirements")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,2, "Sales Requirement Code", StatusValues.Optional, 563)
        ]


CSH = _CSH()


class _PWK(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'PWK', "Paperwork")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2, "Report Type Code", StatusValues.Mandatory, 755),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(1,80, "Description", StatusValues.Optional, 352)
        ]


PWK = _PWK()


class _TD5(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'TD5', "Carrier Details (Routing Sequence/Transit Time)")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,2, "Routing Sequence Code", StatusValues.Optional, 133),
            GenericProperty(1,2,"Identification Code Qualifier", StatusValues.Conditional, 66),
            GenericProperty(2,80, "Identification Code", StatusValues.Conditional, 67),
            GenericProperty(1,2, "Transportation Method/Type Code", StatusValues.Conditional, 91),
            GenericProperty(1,35,"Routing",StatusValues.Conditional,387),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(2,2, "Service Level Code", StatusValues.Conditional, 284)
        ]


TD5 = _TD5()


class _TD4(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'TD4', "Carrier Details (Special Handling, or Hazardous Materials, or Both)")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,3,"Special Handling Code", StatusValues.Conditional, 152)
        ]


TD4 = _TD4()


class _PER(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'PER', "Administrative Communications Contact")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2,"Contact Function Code", StatusValues.Mandatory, 366),
            GenericProperty(1,60, "Name", StatusValues.Optional, 93),
            GenericProperty(2,2, "Communication Number Qualifier", StatusValues.Conditional, 365),
            GenericProperty(1,80, "Communication Number", StatusValues.Conditional, 364),
            GenericProperty(2, 2, "Communication Number Qualifier", StatusValues.Conditional, 365),
            GenericProperty(1,80, "Communication Number", StatusValues.Conditional, 364)
        ]


PER = _PER()


class _PO1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'PO1', "Baseline Item Data")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,20, "Assigned Information", StatusValues.Optional, 350),
            GenericProperty(1,15,"Quantity Ordered", StatusValues.Conditional, 330),
            GenericProperty(2,2,"Unit or Basis for Measurement Code", StatusValues.Optional, 355),
            GenericProperty(1,17,"Unit Price", StatusValues.Conditional,212),
            EmptyProperty(),
            GenericProperty(2,2,"Product/Service ID Qualifier", StatusValues.Conditional,235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Conditional, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Conditional, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Conditional, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Conditional, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Conditional, 234)
        ]


PO1 = _PO1()


class _CTP(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'CTP', "Pricing Information")
        self._append_tag(self)

        self._property_array = [
            EmptyProperty(),
            GenericProperty(3,3,"Price Identifier Code", StatusValues.Conditional, 236),
            GenericProperty(1,17, "Unit Price", StatusValues.Conditional, 212)
        ]


CTP = _CTP()


class _BSN(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'BSN', "Beggining Segment for Ship Notice")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2,"Transaction Set Purpose Code", StatusValues.Mandatory, 353),
            GenericProperty(2,20, "Shipment Identification", StatusValues.Mandatory, 396),
            GenericProperty(8,8,"Date", StatusValues.Mandatory, 373),
            GenericProperty(4,8,"Time", StatusValues.Mandatory, 337),
            GenericProperty(4,4, "Hierarchical Structure Code", StatusValues.Optional, 1005),
            GenericProperty(2,2,"Transaction Type Code", StatusValues.Conditional, 640)
        ]


BSN = _BSN()


class _HL(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'HL', "Hierarchical Level – Shipment")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,12,"Hierarchical ID Number", StatusValues.Mandatory, 628),
            GenericProperty(1,12,"Hierarchical Parent ID Number", StatusValues.Optional, 734),
            GenericProperty(1,2,"Hierarchical Level Code", StatusValues.Mandatory, 735)
        ]


HL = _HL()


class _TD1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'TD1', "Carrier Details (Quantity and Weight)")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(3,5,"Packaging Code", StatusValues.Optional, 103),
            GenericProperty(1,7,"Lading Quantity", StatusValues.Conditional,80),
            EmptyProperty(),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(1,2,"Weight Qualifier",StatusValues.Optional,187),
            GenericProperty(1,10,"Weight", StatusValues.Conditional,81),
            GenericProperty(2,2,"Unit or Basis for Measurement Code", StatusValues.Conditional,355)
        ]


TD1 = _TD1()


class _PRF(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'PRF', "Purchase Order Reference")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(10,10,"Purchase Order Number",StatusValues.Mandatory,324)
        ]


PRF = _PRF()


class _MAN(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'MAN', "Marks and Numbers")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,2,"Marks and Numbers Qualifier", StatusValues.Mandatory, 88),
            GenericProperty(1,48,"Marks and Numbers", StatusValues.Mandatory, 87)
        ]


MAN = _MAN()


class _SN1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'SN1', "Item Detail (Shipment)")
        self._append_tag(self)

        self._property_array = [
            EmptyProperty(),
            GenericProperty(1,10, "Number of Units Shipped", StatusValues.Mandatory, 382),
            GenericProperty(2,2,"Unit or Basis for Measurement Code", StatusValues.Mandatory, 355)
        ]


SN1 = _SN1()


class _BCH(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'BCH', "Beginning Segment for Purchase Order Change")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2, "Transaction Set Purpose Code", StatusValues.Mandatory, 353),
            GenericProperty(2,2, "Purchase Order Type Code", StatusValues.Mandatory, 92),
            GenericProperty(1,22,"Purchase Order Number", StatusValues.Mandatory, 324),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(8,8,"Date",StatusValues.Mandatory,373),
            GenericProperty(8,8,"Date",StatusValues.Optional, 373)
        ]


BCH = _BCH()


class _POC(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'POC', "Line Item Change")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,20,"Assigned Identification", StatusValues.Optional, 350),
            GenericProperty(2,2,"Change or Response Type Code", StatusValues.Mandatory, 670),
            EmptyProperty(),
            EmptyProperty(),
            GenericProperty(2,2,"Unit or Basis for Measurement Code", StatusValues.Mandatory, 355),
            GenericProperty(1,17,"Unit Price", StatusValues.Conditional, 212),
            EmptyProperty(),
            GenericProperty(2,2,"Product/Service ID Qualifier", StatusValues.Conditional, 235),
            GenericProperty(1,48,"Product/Service ID", StatusValues.Conditional, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Conditional, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Conditional, 234),
            GenericProperty(2, 2, "Product/Service ID Qualifier", StatusValues.Conditional, 235),
            GenericProperty(1, 48, "Product/Service ID", StatusValues.Conditional, 234),
        ]


POC = _POC()


class _BAK(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'BAK', "Beginning Segment for Purchase Order Acknowledgment")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2,"Transaction Set Purpose Code", StatusValues.Mandatory, 353),
            GenericProperty(2,2, "Acknowledgment Type", StatusValues.Mandatory, 587),
            GenericProperty(10,10, "Purchase Order Number", StatusValues.Mandatory, 324),
            GenericProperty(8,8, "Date", StatusValues.Mandatory,373)
        ]

BAK = _BAK()


class _CUR(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'CUR', "Currency")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,3, "Entity Identifier Code", StatusValues.Mandatory, 98),
            GenericProperty(3,3, "Currency Code", StatusValues.Mandatory, 100)
        ]


CUR = _CUR()

class _ACK(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'ACK', "Line Item Acknowledgment")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2, 2, "Line Item Status Code", StatusValues.Mandatory, 668),
            GenericProperty(1, 15, "Quantity", StatusValues.Mandatory, 380),
            GenericProperty(2,2, "Unit or Basis for Measurement", StatusValues.Mandatory, 355)
        ]


ACK = _ACK()



class _AK1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'AK1', "Functional Group Response Header")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,2,"Functional Identifier Code", StatusValues.Mandatory, 479),
            GenericProperty(1,9, "Group Control Number", StatusValues.Mandatory, 28)
        ]


AK1 = _AK1()


class _AK2(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'AK2', "Transaction Set Response Header")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(3,3,"Transaction Set Identifier Code", StatusValues.Mandatory, 143),
            GenericProperty(4,9, "Transaction Set Control Number", StatusValues.Mandatory, 329)
        ]



AK2 = _AK2()


class _AK3(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'AK3', "Data Segment Note")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(2,3,"Segment ID Code", StatusValues.Mandatory, 721),
            GenericProperty(1,6,"Segment Position in Transaction Set", StatusValues.Mandatory, 719),
            GenericProperty(1,6,"Loop Identifier Code", StatusValues.Optional, 447),
            GenericProperty(1,3, "Segment Syntax Error Code", StatusValues.Optional, 720)
        ]


AK3 = _AK3()


class _AK4(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'AK4', "Data Element Note")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,2,"Position in Segment", StatusValues.Mandatory,722),
            GenericProperty(1,4,"Data Element Reference Number", StatusValues.Optional, 725),
            GenericProperty(1,3,"Data Element Syntax Error Code", StatusValues.Mandatory, 723),
            GenericProperty(1,99, "Copy of Bad Data Element", StatusValues.Optional, 724)
        ]


AK4 = _AK4()


class _AK5(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'AK5', "Transaction Set Response Trailer")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,1, "Transaction Set Acknowledgment Code", StatusValues.Mandatory, 717),
            GenericProperty(1,3, "Transaction Set Syntax Error Code", StatusValues.Optional, 718),
            GenericProperty(1, 3, "Transaction Set Syntax Error Code", StatusValues.Optional, 718),
            GenericProperty(1, 3, "Transaction Set Syntax Error Code", StatusValues.Optional, 718),
            GenericProperty(1, 3, "Transaction Set Syntax Error Code", StatusValues.Optional, 718),
            GenericProperty(1, 3, "Transaction Set Syntax Error Code", StatusValues.Optional, 718),

        ]


AK5 = _AK5()


class _AK9(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, b'AK9', "Functional Group Response Trailer")
        self._append_tag(self)

        self._property_array = [
            GenericProperty(1,1, "Functional Group Acknowledge Code", StatusValues.Mandatory, 715),
            GenericProperty(1,6, "Number of Transaction Sets Included", StatusValues.Mandatory,97),
            GenericProperty(1,6,"Number of Received Transaction Sets",StatusValues.Mandatory, 123),
            GenericProperty(1,6, "Number of Accepted Transaction Sets", StatusValues.Mandatory, 2),
            GenericProperty(1,3, "Functional Group Syntax Error Code", StatusValues.Optional, 716),
            GenericProperty(1, 3, "Functional Group Syntax Error Code", StatusValues.Optional, 716),
            GenericProperty(1, 3, "Functional Group Syntax Error Code", StatusValues.Optional, 716),
            GenericProperty(1, 3, "Functional Group Syntax Error Code", StatusValues.Optional, 716),
            GenericProperty(1, 3, "Functional Group Syntax Error Code", StatusValues.Optional, 716),

        ]


AK9 = _AK9()