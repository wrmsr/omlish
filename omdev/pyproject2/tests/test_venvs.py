# ruff: noqa: UP006 UP007
import dataclasses as dc
import glob
import json
import typing as ta
import unittest

from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from ...toml import toml_loads
from ..interps import VenvInterps


_TEST_TOML = """
[tool.omlish.pyproject.srcs]
main = [
    'omlish',
    'omdev',
    'ominfra',
    'omserv',
    'app',
]

ml = [
    '@main',
    'omml',
]

all = [
    '@ml',
    'x',
]

[tool.omlish.pyproject.venvs._default]
interp = '@12'
requires = ['requirements-dev.txt']
srcs = ['@main']

[tool.omlish.pyproject.venvs.default]
inherits = ['_default']
requires = ['requirements-ext.txt']

[tool.omlish.pyproject.venvs.'13']
inherits = ['_default']
interp = '@13'

[tool.omlish.pyproject.venvs.'13t']
inherits = ['_default']
interp = '@13t'

[tool.omlish.pyproject.venvs._old]
requires = []
srcs = []

[tool.omlish.pyproject.venvs.'11']
inherits = ['_old']
interp = '@11'

[tool.omlish.pyproject.venvs.'10']
inherits = ['_old']
interp = '@10'

[tool.omlish.pyproject.venvs.'9']
inherits = ['_old']
interp = '@9'

[tool.omlish.pyproject.venvs.'8']
inherits = ['_old']
interp = '@8'

[tool.omlish.pyproject.venvs.docker]
inherits = ['_default']
docker = 'omlish-dev'

[tool.omlish.pyproject.venvs.docker-amd64]
inherits = ['_default']
docker = 'omlish-dev-amd64'

[tool.omlish.pyproject.venvs.deploy]
interp = '3.12'
requires = ['requirements.txt']
"""


@dc.dataclass(frozen=True)
class VenvConfig:
    inherits: ta.Optional[ta.Sequence[str]] = None
    interp: ta.Optional[str] = None
    requires: ta.Optional[ta.List[str]] = None
    docker: ta.Optional[str] = None
    srcs: ta.Optional[ta.List[str]] = None


@dc.dataclass(frozen=True)
class PyprojectConfig:
    srcs: ta.Mapping[str, ta.Sequence[str]]
    venvs: ta.Mapping[str, VenvConfig]


def inherit_venvs(m: ta.Mapping[str, VenvConfig]) -> ta.Mapping[str, VenvConfig]:
    done: ta.Dict[str, VenvConfig] = {}

    def rec(k):
        try:
            return done[k]
        except KeyError:
            pass
        c = m[k]
        kw = dc.asdict(c)
        for i in c.inherits or ():
            ic = rec(i)
            kw.update({k: v for k, v in dc.asdict(ic).items() if v is not None})
        del kw['inherits']
        d = done[k] = VenvConfig(**kw)
        return d

    for k in m:
        rec(k)
    return done


def resolve_srcs(
        lst: ta.Sequence[str],
        aliases: ta.Mapping[str, ta.Sequence[str]],
) -> ta.List[str]:
    todo = list(reversed(lst))
    raw: ta.List[str] = []
    seen: ta.Set[str] = set()
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if not cur.startswith('@'):
            raw.append(cur)
            continue
        todo.extend(aliases[cur[1:]][::-1])
    out: list[str] = []
    seen.clear()
    for r in raw:
        es: list[str]
        if any(c in r for c in '*?'):
            es = list(glob.glob(r, recursive=True))
        else:
            es = [r]
        for e in es:
            if e not in seen:
                seen.add(e)
                out.append(e)
    return out


def fixup_interp(s: ta.Optional[str]) -> ta.Optional[str]:
    if not s or not s.startswith('@'):
        return s
    return VenvInterps().versions_file_pythons()[s[1:]]


class TestVenvs(unittest.TestCase):
    def test_venvs(self):
        def pj(o):
            print(json.dumps(o, indent=2, separators=(', ', ': ')))

        dct = toml_loads(_TEST_TOML)['tool']['omlish']['pyproject']
        pj(dct)

        pcfg: PyprojectConfig = unmarshal_obj(dct, PyprojectConfig)
        print(pcfg)

        ivs = dict(inherit_venvs(pcfg.venvs or {}))
        for k, v in ivs.items():
            v = dc.replace(v, srcs=resolve_srcs(v.srcs or [], pcfg.srcs or {}))
            v = dc.replace(v, interp=fixup_interp(v.interp))
            ivs[k] = v

        pj(marshal_obj(ivs))
