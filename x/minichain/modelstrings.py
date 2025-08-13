"""
NOTES:
 - DO want to be able to cram a model spec into a string, like a db conn str, for argparse
  - dbapi, standardize my own conn str?
   - it uses a url
 - mini language - ideally regexable
  - inline json?
 - engine:repo/model
 - at signs for aliases? where?
 - 'piping'?
 - service type
 - conversion to / generation of Config tv's
 - huggingface handle 'tag dir is a file containing a rev'
 - ** make them manifest-able, yaml-able **
"""
import os.path
import re
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.algorithm.toposort import mut_toposort
from ommlds import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class ParsedBackendString:
    backend: str | None = None

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
        backend, s = s.split(':')
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
            path=m.group('path')
        )

    else:
        model = ParsedBackendString.NameModel(s)

    return ParsedBackendString(
        backend=backend,
        model=model,
    )


##


def test_backend_strings():
    assert parse_backend_string('gpt-3.5-turbo') == ParsedBackendString(model=ParsedBackendString.NameModel('gpt-3.5-turbo'))

    assert parse_backend_string('openai') == ParsedBackendString(model=ParsedBackendString.NameModel('openai'))

    assert parse_backend_string('openai:gpt-3.5-turbo') == ParsedBackendString(
        backend='openai',
        model=ParsedBackendString.NameModel('gpt-3.5-turbo'),
    )

    assert parse_backend_string('mlx:mlx-community/Qwen2.5-0.5B-4bit') == ParsedBackendString(
        backend='mlx',
        model=ParsedBackendString.RepoModel('mlx-community', 'Qwen2.5-0.5B-4bit'),
    )

    assert parse_backend_string(
        'llamacpp:~/.cache/huggingface/hub/models--QuantFactory--Meta-Llama-3-8B-GGUF/'
        'snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',
    ) == ParsedBackendString(
        backend='llamacpp',
        model=ParsedBackendString.PathModel(
            os.path.expanduser('~/.cache/huggingface/hub/models--QuantFactory--Meta-Llama-3-8B-GGUF/'
            'snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf'),
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


##


def instantiate_backend_string(
        service_cls: ta.Any,
        ps: ParsedBackendString,
        *args: ta.Any,
        **kwargs: ta.Any,
) -> ta.Any:
    be_name: str
    be_cfg: ta.Sequence[mc.Config]

    be_name = check.not_none(ps.backend)
    be_cfg = [
        mc.ModelName(check.isinstance(ps.model, ParsedBackendString.NameModel).name),
    ]

    return mc.registry_new(
        service_cls,
        be_name,
        *be_cfg,
        *args,
        **kwargs,
    )


def test_instantiate_backend_strings():
    svc = instantiate_backend_string(
        'ChatChoicesService',
        parse_backend_string('anthropic:claude-3-7-sonnet-latest'),
        mc.ApiKey('abcd'),
    )
    print(svc)


##


@dc.dataclass(frozen=True)
class ModelNameBackendStringPack:
    service_cls: str | ta.Any | ta.AbstractSet[str] | ta.AbstractSet[ta.Any]

    default_model_name: str

    _: dc.KW_ONLY

    model_name_aliases: ta.Mapping[str, str] | None = None

    @cached.property
    def model_name_alias_map(self) -> ta.Mapping[str, str]:
        if not (src := self.model_name_aliases):
            return {}

        dct: dict[str, str] = {}
        for ks in mut_toposort({k: {v} for k, v in src.items()}):
            for k in ks:
                dct[k] = dct.get(src.get(k, k), k)
        return dct

    @cached.property
    def root_model_names(self) -> frozenset[str]:
        return frozenset(self.model_name_alias_map.values())


ANTHROPIC_MODEL_NAME_BACKEND_STRING_PACK = ModelNameBackendStringPack(
    mc.ChatChoicesService,
    'anthropic',
    model_name_aliases={
        'claude-opus-4-1': 'claude-opus-4-1-20250805',
        'claude-opus': 'claude-opus-4-1',

        'claude-sonnet-4': 'claude-sonnet-4-20250514',
        'claude-sonnet': 'claude-sonnet-4',

        'claude-haiku-3-5': 'claude-haiku-3-5-latest',
        'claude-haiku': 'claude-haiku-3-5',

        'claude': 'claude-haiku',
    },
)

# OPENAI_MODEL_NAME_BACKEND_STRING_PACK = ModelNameBackendStringPack(
#
# )
