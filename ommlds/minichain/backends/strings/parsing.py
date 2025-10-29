import os.path
import re

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class ParsedBackendString:
    backend: str | None = dc.xfield(None, repr_fn=dc.opt_repr)

    #

    @dc.dataclass(frozen=True)
    class Model(lang.Abstract, lang.Sealed):
        pass

    @dc.dataclass(frozen=True)
    class NameModel(Model, lang.Final):
        name: str

        def __post_init__(self) -> None:
            check.non_empty_str(self.name)

    @dc.dataclass(frozen=True)
    class PathModel(Model, lang.Final):
        path: str

        def __post_init__(self) -> None:
            check.non_empty_str(self.path)

    @dc.dataclass(frozen=True)
    class RepoModel(Model, lang.Final):
        namespace: str
        repo: str

        _: dc.KW_ONLY

        tag: str | None = None
        path: str | None = None

    model: Model


_REPO_MODEL_PAT = re.compile(
    r'(?P<namespace>[^/]+)/(?P<repo>[^@/]+)'
    r'(@(?P<tag>[^/]+))?'
    r'(/(?P<path>.+))?',
)


def parse_backend_string(s: str) -> ParsedBackendString:
    backend: str | None
    if ':' in s:
        backend, _, s = s.partition(':')
    else:
        backend = None

    model: ParsedBackendString.Model

    if any(s.startswith(c) for c in '~./'):
        model = ParsedBackendString.PathModel(os.path.expanduser(s))

    elif '/' in s:
        m = check.not_none(_REPO_MODEL_PAT.fullmatch(s))
        model = ParsedBackendString.RepoModel(
            m.group('namespace'),
            m.group('repo'),
            tag=m.group('tag'),
            path=m.group('path'),
        )

    else:
        model = ParsedBackendString.NameModel(s)

    return ParsedBackendString(
        backend=backend,
        model=model,
    )
