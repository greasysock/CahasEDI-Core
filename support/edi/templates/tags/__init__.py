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
    def __init__(self, min_length : int, max_length : int, name, status : StatusValues, tag : int):
        self._min_length = min_length
        self._max_length = max_length
        self._name = name
        self._status = status
        self._tag = tag

        self._content = None

    def set_content(self, content):
        self._content = content

    def __str__(self):
        return " [ {}: \"{}\" ] ".format(self._name, self._content.decode("utf-8"))


class GENERIC_TAG:
    _tags = list()
    def __init__(self, tag, content, status = StatusValues.Mandatory , max_occ = 1, level = 0):
        self._counter = None
        self._no = None
        self._tag = tag
        self._status = status
        self._max_occ = max_occ
        self._level = level
        self._content = content
        self._property_array = list()

    def _append_tag(self, tag_obj):
        self._tags.append(tag_obj)

    @property
    def status(self):
        return self._status

    @property
    def max_occ(self):
        return self._max_occ

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

    def put_bytes_list(self, bytes_list : list):
        print(self._tag)
        for i,value in enumerate(bytes_list):
            self._property_array[i].set_content(value)
            print(self._property_array[i])


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
        GENERIC_TAG.__init__(self, "BIG", "Beginning Segment for Invoice")
        self._append_tag(self)


BIG = _BIG()


class _REF(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "REF", "Reference Identification")
        self._append_tag(self)


REF = _REF()


class _N1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "N1", "Name")
        self._append_tag(self)


N1 = _N1()


class _N3(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "N3", "Address Information")
        self._append_tag(self)


N3 = _N3()


class _N4(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "N4", "Geographic Location")
        self._append_tag(self)


N4 = _N4()


class _ITD(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "ITD", "Terms of Sale/Deterred Terms of Sale")
        self._append_tag(self)


ITD = _ITD()


class _DTM(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "DTM", "Date/Time Reference")
        self._append_tag(self)


DTM = _DTM()


class _FOB(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "FOB", "F.O.B. Related Instructions")
        self._append_tag(self)


FOB = _FOB()


class _IT1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "IT1", "Baseline Item Data (Invoice)")
        self._append_tag(self)


IT1 = _IT1()


class _PID(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "PID", "Product/Item Description")
        self._append_tag(self)


PID = _PID()


class _SAC(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "SAC", "Sevice, Promotion, Allowance, or Charge Information")
        self._append_tag(self)


SAC = _SAC()


class _TXI(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "TXI", "Tax Information")
        self._append_tag(self)


TXI = _TXI()


class _TDS(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "TDS", "Total Monetary Value Summary")
        self._append_tag(self)


TDS = _TDS()


class _CAD(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "CAD", "Carrier Detail")
        self._append_tag(self)


CAD = _CAD()


class _AMT(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "AMT", "Monetary Amount")
        self._append_tag(self)


AMT = _AMT()


class _CTT(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "CTT", "Transaction Totals")
        self._append_tag(self)


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
        GENERIC_TAG.__init__(self, "BIA", "Beginning Segment for Inventory Inquiry/Advice")
        self._append_tag(self)


BIA = _BIA()


class _LIN(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "LIN", "Item Identification")
        self._append_tag(self)


LIN = _LIN()


class _QTY(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "QTY", "Quantity Available")
        self._append_tag(self)


QTY = _QTY()


class _SCH(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "SCH", "Line Item Schedule")
        self._append_tag(self)


SCH = _SCH()


class _CSH(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "CSH", "Sales Requirements")
        self._append_tag(self)


CSH = _CSH()


class _PWK(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "PWK", "Paperwork")
        self._append_tag(self)


PWK = _PWK()


class _TD5(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "TD5", "Carrier Details (Routing Sequence/Transit Time)")
        self._append_tag(self)


TD5 = _TD5()


class _TD4(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "TD4", "Carrier Details (Special Handling, or Hazardous Materials, or Both)")
        self._append_tag(self)


TD4 = _TD4()


class _PER(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "PER", "Administrative Communications Contact")
        self._append_tag(self)


PER = _PER()


class _PO1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "PO1", "Baseline Item Data")
        self._append_tag(self)


PO1 = _PO1()


class _CTP(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "CTP", "Pricing Information")
        self._append_tag(self)


CTP = _CTP()


class _BSN(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "BSN", "Beggining Segment for Ship Notice")
        self._append_tag(self)


BSN = _BSN()


class _HL(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "HL", "Hierarchical Level – Shipment")
        self._append_tag(self)


HL = _HL()


class _TD1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "TD1", "Carrier Details (Quantity and Weight)")
        self._append_tag(self)


TD1 = _TD1()


class _PRF(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "PRF", "Purchase Order Reference")
        self._append_tag(self)


PRF = _PRF()


class _MAN(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "MAN", "Marks and Numbers")
        self._append_tag(self)


MAN = _MAN()


class _SN1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "SN1", "Item Detail (Shipment)")
        self._append_tag(self)


SN1 = _SN1()


class _BCH(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "BCH", "Beggining Segment for Purchase Order Change")
        self._append_tag(self)


BCH = _BCH()


class _POC(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "POC", "Line Item Change")
        self._append_tag(self)


POC = _POC()


class _BAK(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "BAK", "Beggining Segment for Purchase Order Aknowledgment")
        self._append_tag(self)


BAK = _BAK()


class _CUR(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "CUR", "Currency")
        self._append_tag(self)


CUR = _CUR()


class _AK1(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "AK1", "Functional Group Response Header")
        self._append_tag(self)


AK1 = _AK1()


class _AK2(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "AK2", "Transaction Set Response Header")
        self._append_tag(self)


AK2 = _AK2()


class _AK3(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "AK3", "Data Segment Note")
        self._append_tag(self)


AK3 = _AK3()


class _AK4(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "AK4", "Data Element Note")
        self._append_tag(self)


AK4 = _AK4()


class _AK5(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "AK5", "Transaction Set Response Trailer")
        self._append_tag(self)


AK5 = _AK5()


class _AK9(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "AK9", "Functional Group Response Trailer")
        self._append_tag(self)


AK9 = _AK9()