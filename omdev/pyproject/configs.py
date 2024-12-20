# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.marshal import unmarshal_obj

from ..interp.venvs import InterpVenvConfig


@dc.dataclass(frozen=True)
class VenvConfig(InterpVenvConfig):
    inherits: ta.Optional[ta.Sequence[str]] = None
    docker: ta.Optional[str] = None
    srcs: ta.Optional[ta.List[str]] = None


@dc.dataclass(frozen=True)
class PyprojectConfig:
    pkgs: ta.Sequence[str] = dc.field(default_factory=list)
    srcs: ta.Mapping[str, ta.Sequence[str]] = dc.field(default_factory=dict)
    venvs: ta.Mapping[str, VenvConfig] = dc.field(default_factory=dict)

    venvs_dir: str = '.venvs'
    versions_file: ta.Optional[str] = '.versions'


class PyprojectConfigPreparer:
    def __init__(
            self,
            *,
            python_versions: ta.Optional[ta.Mapping[str, str]] = None,
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
                kw.update({k: v for k, v in dc.asdict(ic).items() if v is not None and kw.get(k) is None})
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

        pcfg = dc.replace(pcfg, venvs=ivs)
        return pcfg
