import dataclasses as dc  # noqa
import typing as ta
import weakref  # noqa


def marshal_obj(o: ta.Any) -> ta.Any:
    return o


def unmarshal_obj(o: ta.Any) -> ta.Any:
    return o
