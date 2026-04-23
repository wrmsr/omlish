"""
TODO:
 - re-introduce (better) terse parsing
  - use abnf
  - interpret s[0] in '/~.' as path

====

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

"""
# from omlish import check
# from omlish import marshal as msh
# from omlish.formats import json5
#
# from .types import BackendSpec
# from .types import ModelBackendSpec
#
#
# ##
#
#
# def parse_backend_spec(s: str) -> BackendSpec:
#     s = check.non_empty_str(s.strip())
#
#     if s.startswith('{'):
#         return msh.unmarshal(json5.loads(s), BackendSpec)
#
#     return ModelBackendSpec(s)
