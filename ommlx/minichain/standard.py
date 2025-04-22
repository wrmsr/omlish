"""
TODO:
 - DefaultOptions
"""
from omlish import dataclasses as dc
from omlish import typedvalues as tv
from omlish.secrets import all as sec

from .config import Config


##


class ModelName(Config, tv.UniqueScalarTypedValue[str]):
    pass


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ApiKey(Config, tv.UniqueTypedValue):
    v: sec.SecretRefOrStr = dc.field() | sec.secret_field
