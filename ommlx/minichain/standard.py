# ruff: noqa: UP006
import os
import typing as ta

from omlish import dataclasses as dc
from omlish import typedvalues as tv
from omlish.secrets import all as sec

from .configs import Config
from .services import RequestOption


##


class ModelName(Config, tv.UniqueScalarTypedValue[str]):
    pass


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ApiKey(Config, tv.UniqueTypedValue):
    v: sec.SecretRefOrStr = dc.field() | sec.secret_field

    @classmethod
    def pop_secret(
            cls,
            consumer: tv.TypedValuesConsumer,
            default: ta.Union[
                'ApiKey',
                sec.Secret,
                sec.SecretRef,
                str,
                ta.Callable[[], sec.Secret | str | None],
                None,
            ] = None,
            *,
            env: str | None = None,
    ) -> sec.Secret | None:
        if (ak := consumer.pop(cls, None)) is not None:
            if isinstance(ak.v, str):
                return sec.Secret.of(ak.v)
            elif isinstance(ak.v, sec.SecretRef):
                raise NotImplementedError
            else:
                raise TypeError(ak.v)

        if default is not None:
            dv: ta.Any = default
            if isinstance(dv, cls):
                dv = dv.v
            elif callable(dv):
                dv = dv()

            if isinstance(dv, sec.Secret):
                return dv
            elif isinstance(dv, str):
                return sec.Secret.of(dv)
            elif dv is not None:
                raise TypeError(dv)

        if env is not None:
            if (ev := os.environ.get(env)) is not None:
                return sec.Secret.of(ev)

        return None


##


class DefaultRequestOptions(Config, tv.ScalarTypedValue[ta.Sequence[RequestOption]]):
    pass
