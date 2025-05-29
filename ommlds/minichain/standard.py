# ruff: noqa: UP006 UP007
import os
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv
from omlish.secrets import all as sec

from .configs import Config
from .services import RequestOption


RequestOptionT = ta.TypeVar('RequestOptionT', bound=RequestOption)


##


class ModelSpecifier(Config, tv.UniqueTypedValue, lang.Abstract):
    pass


class ModelName(tv.ScalarTypedValue[str], ModelSpecifier):
    pass


class ModelPath(tv.ScalarTypedValue[str], ModelSpecifier):
    pass


##


class Device(tv.UniqueScalarTypedValue[ta.Any], Config):
    pass


##


@dc.dataclass(frozen=True)
class SecretConfig(Config, lang.Abstract):
    v: sec.SecretRefOrStr = dc.field() | sec.secret_field

    @classmethod
    def pop_secret(
            cls,
            consumer: tv.TypedValuesConsumer,
            default: ta.Union[
                ta.Self,
                sec.Secret,
                sec.SecretRef,
                str,
                ta.Callable[[], sec.Secret | str | None],
                None,
            ] = None,
            *,
            env: str | None = None,
    ) -> sec.Secret | None:
        check.issubclass(cls, tv.UniqueTypedValue)

        if (ak := consumer.pop(cls, None)) is not None:  # type: ignore[type-var]
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


#


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ApiKey(SecretConfig, tv.UniqueTypedValue):
    pass


##


class DefaultRequestOptions(Config, tv.ScalarTypedValue[ta.Sequence[RequestOptionT]]):
    @dc.init
    def _check_arg(self) -> None:
        for e in check.isinstance(self.v, ta.Sequence):
            check.isinstance(e, RequestOption)

    @classmethod
    def pop(cls, consumer: tv.TypedValuesConsumer) -> tv.TypedValues[RequestOptionT]:
        return tv.TypedValues(*[
            o
            for dro in consumer.pop(cls, [])
            for o in dro.v
        ])
