import uuid

from omlish import typedvalues as tv


##


class ChatDriverId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass
