# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - smarter merging than just dumb dict-squashing
"""
import typing as ta

from ..types import ConfigMap


##


def merge_configs(*ms: ConfigMap) -> ConfigMap:
    def rec(o, i):
        for k, v in i.items():
            try:
                e = o[k]
            except KeyError:
                o[k] = v
            else:
                if isinstance(e, ta.Mapping) and isinstance(v, ta.Mapping):
                    rec(e, v)  # noqa
                else:
                    if isinstance(v, ta.Mapping):
                        v = dict(v)
                    o[k] = v

    o: dict = {}
    for i in ms:
        rec(o, i)
    return o
