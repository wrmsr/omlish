import uuid

from omlish import typedvalues as tv


##


class ChatId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass
