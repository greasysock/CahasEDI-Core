class GenericGroupId:
    def __init__(self, identifier_code: bytes, description: str):
        self._identifier_code = identifier_code
        self._description = description

    @property
    def identifier_code(self):
        return self._identifier_code
    @property
    def description(self):
        return self._description


class Invoice(GenericGroupId):
    def __init__(self):
        GenericGroupId.__init__(self, b'IN', 'Invoice')


class PurchaseOrder(GenericGroupId):
    def __init__(self):
        GenericGroupId.__init__(self, b'PO', 'Purchase Order')


class PurchaseOrderAcknowledgement(GenericGroupId):
    def __init__(self):
        GenericGroupId.__init__(self, b'PR', 'Purchase Order Acknowledgment')


class ShipNotice(GenericGroupId):
    def __init__(self):
        GenericGroupId.__init__(self, b'SH', 'Ship Notice')


class PurchaseOrderChange(GenericGroupId):
    def __init__(self):
        GenericGroupId.__init__(self, b'PC', 'Purchase Order Change Request')


class FunctionalAcknowledgement(GenericGroupId):
    def __init__(self):
        GenericGroupId.__init__(self, b'FA', 'Functional Acknowledgment')
