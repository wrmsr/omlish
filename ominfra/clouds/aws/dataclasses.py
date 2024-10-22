# ruff: noqa: UP006 UP007
# @omlish-lite
import collections.abc
import dataclasses as dc
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.reflect import get_optional_alias_arg
from omlish.lite.reflect import is_generic_alias
from omlish.lite.reflect import is_optional_alias
from omlish.lite.strings import camel_case


class AwsDataclass:
    class Raw(dict):
        pass

    #

    _aws_meta: ta.ClassVar[ta.Optional['AwsDataclassMeta']] = None

    @classmethod
    def _get_aws_meta(cls) -> 'AwsDataclassMeta':
        try:
            return cls.__dict__['_aws_meta']
        except KeyError:
            pass
        ret = cls._aws_meta = AwsDataclassMeta(cls)
        return ret

    #

    def to_aws(self) -> ta.Mapping[str, ta.Any]:
        return self._get_aws_meta().converters().d2a(self)

    @classmethod
    def from_aws(cls, v: ta.Mapping[str, ta.Any]) -> 'AwsDataclass':
        return cls._get_aws_meta().converters().a2d(v)


@dc.dataclass(frozen=True)
class AwsDataclassMeta:
    cls: ta.Type['AwsDataclass']

    #

    class Field(ta.NamedTuple):
        d_name: str
        a_name: str
        is_opt: bool
        is_seq: bool
        dc_cls: ta.Optional[ta.Type['AwsDataclass']]

    @cached_nullary
    def fields(self) -> ta.Sequence[Field]:
        fs = []
        for f in dc.fields(self.cls):  # type: ignore  # noqa
            d_name = f.name
            a_name = camel_case(d_name, lower=True)

            is_opt = False
            is_seq = False
            dc_cls = None

            c = f.type
            if c is AwsDataclass.Raw:
                continue

            if is_optional_alias(c):
                is_opt = True
                c = get_optional_alias_arg(c)

            if is_generic_alias(c) and ta.get_origin(c) is collections.abc.Sequence:
                is_seq = True
                [c] = ta.get_args(c)

            if is_generic_alias(c):
                raise TypeError(c)

            if isinstance(c, type) and issubclass(c, AwsDataclass):
                dc_cls = c

            fs.append(AwsDataclassMeta.Field(
                d_name=d_name,
                a_name=a_name,
                is_opt=is_opt,
                is_seq=is_seq,
                dc_cls=dc_cls,
            ))

        return fs

    #

    class Converters(ta.NamedTuple):
        d2a: ta.Callable
        a2d: ta.Callable

    @cached_nullary
    def converters(self) -> Converters:
        for df in dc.fields(self.cls):  # type: ignore  # noqa
            c = df.type

            if is_optional_alias(c):
                c = get_optional_alias_arg(c)

            if c is AwsDataclass.Raw:
                rf = df.name
                break

        else:
            rf = None

        fs = [
            (f, f.dc_cls._get_aws_meta().converters() if f.dc_cls is not None else None)  # noqa
            for f in self.fields()
        ]

        def d2a(o):
            dct = {}
            for f, cs in fs:
                x = getattr(o, f.d_name)
                if x is None:
                    continue
                if cs is not None:
                    if f.is_seq:
                        x = list(map(cs.d2a, x))
                    else:
                        x = cs.d2a(x)
                dct[f.a_name] = x
            return dct

        def a2d(v):
            dct = {}
            for f, cs in fs:
                x = v.get(f.a_name)
                if x is None:
                    continue
                if cs is not None:
                    if f.is_seq:
                        x = list(map(cs.a2d, x))
                    else:
                        x = cs.a2d(x)
                dct[f.d_name] = x
            if rf is not None:
                dct[rf] = self.cls.Raw(v)
            return self.cls(**dct)

        return AwsDataclassMeta.Converters(d2a, a2d)
