# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - custom merging by key - replace, append, setdefault, equality enforcement, ...
 - better handling of 'None' as signal to replace or not
 - remove inherited
"""
import typing as ta

from ..types import ConfigMap


##


def build_config_inherited_values(
        m: ta.Mapping[str, ConfigMap],
        *,
        inherits_key: str = 'inherits',
) -> ta.Dict[str, ConfigMap]:
    done: ta.Dict[str, ConfigMap] = {}

    def rec(mk: str) -> ta.Mapping[str, ConfigMap]:
        try:
            return done[mk]
        except KeyError:
            pass

        cur = m[mk]
        try:
            inh_seq = cur[inherits_key]
        except KeyError:
            done[mk] = cur
            return cur

        new = dict(cur)
        for inh in inh_seq:
            inh_dct = rec(inh)
            new.update({
                k: v
                for k, v in inh_dct.items()
                if v is not None
                and cur.get(k) is None
            })

        out = {
            k: v
            for k, v in new.items()
            if k != inherits_key
        }

        done[mk] = out
        return out

    for mk in m:
        rec(mk)
    return done
