from omlish import dataclasses as dc
from omlish import typedvalues as tv

from ....standard import SecretConfig


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class HuggingfaceHubToken(SecretConfig, tv.UniqueTypedValue):
    pass
