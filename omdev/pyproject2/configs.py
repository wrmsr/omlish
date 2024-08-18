import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.marshal import unmarshal_obj


@dc.dataclass(frozen=True)
class VersionsFile:
    name: ta.Optional[str] = '.versions'

    @cached_nullary
    def contents(self) -> ta.Mapping[str, str]:
        if not self.name or not os.path.exists(self.name):
            return {}
        with open(self.name) as f:
            lines = f.readlines()
        return {
            k: v
            for l in lines
            if (sl := l.split('#')[0].strip())
            for k, _, v in (sl.partition('='),)
        }

    @cached_nullary
    def pythons(self) -> ta.Mapping[str, str]:
        raw_vers = self.contents()
        pfx = 'PYTHON_'
        return {k[len(pfx):].lower(): v for k, v in raw_vers.items() if k.startswith(pfx)}


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


class PyprojectConfigPreparer:
    def __init__(
            self,
            *,
            python_versions: ta.Optional[ta.Mapping[str, str]],
    ) -> None:
        super().__init__()

        self._python_versions = python_versions or {}

    def _inherit_venvs(self, m: ta.Mapping[str, VenvConfig]) -> ta.Mapping[str, VenvConfig]:
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

    def _resolve_srcs(
            self,
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
        return raw

    def _fixup_interp(self, s: ta.Optional[str]) -> ta.Optional[str]:
        if not s or not s.startswith('@'):
            return s
        return self._python_versions[s[1:]]

    def prepare_config(self, dct: ta.Mapping[str, ta.Any]) -> PyprojectConfig:
        pcfg: PyprojectConfig = unmarshal_obj(dct, PyprojectConfig)

        ivs = dict(self._inherit_venvs(pcfg.venvs or {}))
        for k, v in ivs.items():
            v = dc.replace(v, srcs=self._resolve_srcs(v.srcs or [], pcfg.srcs or {}))
            v = dc.replace(v, interp=self._fixup_interp(v.interp))
            ivs[k] = v

        return pcfg
