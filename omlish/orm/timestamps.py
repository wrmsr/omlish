from .. import lang
from .. import typedvalues as tv
from .fields import FieldOption


##


class Timestamp(FieldOption, tv.UniqueTypedValue, lang.Abstract, lang.Sealed):
    pass


class CreatedAt(Timestamp, lang.Final):
    pass


class UpdatedAt(Timestamp, lang.Final):
    pass
