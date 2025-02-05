# ruff: noqa: UP006 UP007
"""
TODO:
 - generate to nginx config
"""
import dataclasses as dc
import typing as ta

from omlish.lite.check import check

from .targets import DataServerTarget


##


@dc.dataclass(frozen=True)
class DataServerRoute:
    paths: ta.Sequence[str]
    target: DataServerTarget

    @classmethod
    def of(cls, obj: ta.Union[
        'DataServerRoute',
        ta.Tuple[
            ta.Union[str, ta.Iterable[str]],
            DataServerTarget,
        ],
    ]) -> 'DataServerRoute':
        if isinstance(obj, cls):
            return obj

        elif isinstance(obj, tuple):
            p, t = obj

            if isinstance(p, str):
                p = [p]

            return cls(
                paths=tuple(p),
                target=check.isinstance(t, DataServerTarget),
            )

        else:
            raise TypeError(obj)

    @classmethod
    def of_(cls, *objs: ta.Any) -> ta.List['DataServerRoute']:
        return [cls.of(obj) for obj in objs]
