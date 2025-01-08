import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang


DateTime = ta.NewType('DateTime', str)
MillisecondDateTime = ta.NewType('MillisecondDateTime', str)

Timestamp = ta.NewType('Timestamp', str)


##


class TagList:
    pass


##


class MEMBER_NAME(lang.Marker):  # noqa
    pass


class SHAPE_NAME(lang.Marker):  # noqa
    pass


##


def common_metadata(
        *,
        shape_name: str | None = None,
) -> dict[ta.Any, ta.Any]:
    md = {}

    if shape_name is not None:
        md[SHAPE_NAME] = shape_name

    return md


##


def shape_metadata(
        **kwargs: ta.Any,
) -> dict[ta.Any, ta.Any]:
    md = {**common_metadata(**kwargs)}

    return md


@dc.dataclass(frozen=True)
class Shape:
    __shape_metadata__: ta.ClassVar[ta.Mapping[ta.Any, ta.Any]]

    def __init_subclass__(
            cls,
            *,
            shape_name: str | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        check.state(not hasattr(cls, '__shape_metadata__'))

        cls.__shape_metadata__ = shape_metadata(**kwargs)


##


def field_metadata(
        *,
        member_name: str | None = None,
        **kwargs: ta.Any,
) -> dict[ta.Any, ta.Any]:
    md = {**common_metadata(**kwargs)}

    if member_name is not None:
        md[MEMBER_NAME] = member_name

    return md


##


@dc.dataclass(frozen=True, eq=False, kw_only=True)
class Operation:
    name: str

    input: type[Shape] | None = None
    output: type[Shape] | None = None

    errors: ta.Sequence[type[Shape]] | None = None
