from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ..json import JsonValue
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
@msh.update_fields_options(['v'], marshal_as=JsonValue, unmarshal_as=JsonValue)
class JsonContent(StandardContent, lang.Final):
    v: JsonValue
