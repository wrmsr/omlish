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

====

def test_backend_strings():
    assert parse_backend_string('gpt-3.5-turbo') == ParsedBackendString(
        model=ParsedBackendString.NameModel('gpt-3.5-turbo'),
    )

    assert parse_backend_string('openai') == ParsedBackendString(
        model=ParsedBackendString.NameModel('openai'),
    )

    assert parse_backend_string('openai:gpt-3.5-turbo') == ParsedBackendString(
        backend='openai',
        model=ParsedBackendString.NameModel('gpt-3.5-turbo'),
    )

    assert parse_backend_string('mlx:mlx-community/Qwen2.5-0.5B-4bit') == ParsedBackendString(
        backend='mlx',
        model=ParsedBackendString.RepoModel('mlx-community', 'Qwen2.5-0.5B-4bit'),
    )

    assert parse_backend_string(
        ':'.join(['llamacpp', the_path := (
            '~/.cache/huggingface/hub/models--QuantFactory--Meta-Llama-3-8B-GGUF/'
            'snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf'
        )]),
    ) == ParsedBackendString(
        backend='llamacpp',
        model=ParsedBackendString.PathModel(
            os.path.expanduser(the_path),
        ),
    )

    assert parse_backend_string(
        'llamacpp:QuantFactory/Meta-Llama-3-8B-GGUF@1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',
    ) == ParsedBackendString(
        backend='llamacpp',
        model=ParsedBackendString.RepoModel(
            namespace='QuantFactory',
            repo='Meta-Llama-3-8B-GGUF',
            tag='1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
            path='Meta-Llama-3-8B.Q8_0.gguf',

        ),
    )

    assert parse_backend_string(
        'llamacpp:QuantFactory/Meta-Llama-3-8B-GGUF/Meta-Llama-3-8B.Q8_0.gguf',
    ) == ParsedBackendString(
        backend='llamacpp',
        model=ParsedBackendString.RepoModel(
            namespace='QuantFactory',
            repo='Meta-Llama-3-8B-GGUF',
            path='Meta-Llama-3-8B.Q8_0.gguf',
        ),
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
