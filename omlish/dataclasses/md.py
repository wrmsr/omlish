import typing as ta

from .. import lang


METADATA_KEY = '__dataclass_metadata__'


def _add_cls_md(k, v):
    lang.get_caller_cls_dct(1).setdefault(METADATA_KEY, {}).setdefault(k, []).append(v)


##


class Check(lang.Marker):
    pass


def check(fn: ta.Union[ta.Callable[..., bool], staticmethod]) -> None:
    _add_cls_md(Check, fn)


##


class Init(lang.Marker):
    pass


def init(fn: ta.Union[ta.Callable[..., bool], staticmethod]) -> None:
    _add_cls_md(Init, fn)
