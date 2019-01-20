# Classes and methods that control, verify, and read incoming and outgoing edi files.

def get_tags():
    t = ISA.get_tags()
    return t

class GENERIC_TAG:
    _tags = list()
    def __init__(self, tag, content):
        self._counter = None
        self._no = None
        self._tag = tag
        self._st = None
        self._max_occ = None
        self._level = None
        self._content = content

    def _append_tag(self, tag_obj):
        self._tags.append(tag_obj)

    @property
    def tag(self):
        return self._tag

    @property
    def content(self):
        return self._content

    def get_tags(self):
        return self._tags


class _ISA(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "ISA", "Interchange Control Header")
        self._append_tag(self)


ISA = _ISA()


class _GS(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "GS", "Functional Group Header")
        self._append_tag(self)


GS = _GS()


class _ST(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "ST", "Transaction Set Header")
        self._append_tag(self)


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
        GENERIC_TAG.__init__(self, "SE", "Transaction Set Trailer")
        self._append_tag(self)


SE = _SE()


class _GE(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "GE", "Transaction Group Trailer")
        self._append_tag(self)


GE = _GE()


class _IEA(GENERIC_TAG):
    def __init__(self):
        GENERIC_TAG.__init__(self, "IEA", "Interchange Control Trailer")
        self._append_tag(self)


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