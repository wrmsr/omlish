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
"""
import dataclasses as dc
import os.path
import re

from omlish import check
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class ParsedModelString:
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


_REPO_MODEL_PAT = re.compile(r'(?P<namespace>[^/]+)/(?P<repo>[^@/]+)(@(?P<tag>[^/]+))?(/(?P<path>.+))?')


def parse_model_string(s: str) -> ParsedModelString:
    backend: str | None
    if ':' in s:
        backend, s = s.split(':')
    else:
        backend = None

    model: ParsedModelString.Model

    if any(s.startswith(c) for c in '~./'):
        model = ParsedModelString.PathModel(os.path.expanduser(s))

    elif '/' in s:
        m = check.not_none(_REPO_MODEL_PAT.fullmatch(s))
        model = ParsedModelString.RepoModel(
            m.group('namespace'),
            m.group('repo'),
            tag=m.group('tag'),
            path=m.group('path')
        )

    else:
        model = ParsedModelString.NameModel(s)

    return ParsedModelString(
        backend=backend,
        model=model,
    )


##


def test_model_strings():
    assert parse_model_string('gpt-3.5-turbo') == ParsedModelString(model=ParsedModelString.NameModel('gpt-3.5-turbo'))

    assert parse_model_string('openai') == ParsedModelString(model=ParsedModelString.NameModel('openai'))

    assert parse_model_string('openai:gpt-3.5-turbo') == ParsedModelString(
        backend='openai',
        model=ParsedModelString.NameModel('gpt-3.5-turbo'),
    )

    assert parse_model_string('mlx:mlx-community/Qwen2.5-0.5B-4bit') == ParsedModelString(
        backend='mlx',
        model=ParsedModelString.RepoModel('mlx-community', 'Qwen2.5-0.5B-4bit'),
    )

    assert parse_model_string(
        'llamacpp:~/.cache/huggingface/hub/models--QuantFactory--Meta-Llama-3-8B-GGUF/'
        'snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',
    ) == ParsedModelString(
        backend='llamacpp',
        model=ParsedModelString.PathModel(
            os.path.expanduser('~/.cache/huggingface/hub/models--QuantFactory--Meta-Llama-3-8B-GGUF/'
            'snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf'),
        ),
    )

    assert parse_model_string(
        'llamacpp:QuantFactory/Meta-Llama-3-8B-GGUF@1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',
    ) == ParsedModelString(
        backend='llamacpp',
        model=ParsedModelString.RepoModel(
            namespace='QuantFactory',
            repo='Meta-Llama-3-8B-GGUF',
            tag='1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
            path='Meta-Llama-3-8B.Q8_0.gguf',

        ),
    )

    assert parse_model_string(
        'llamacpp:QuantFactory/Meta-Llama-3-8B-GGUF/Meta-Llama-3-8B.Q8_0.gguf',
    ) == ParsedModelString(
        backend='llamacpp',
        model=ParsedModelString.RepoModel(
            namespace='QuantFactory',
            repo='Meta-Llama-3-8B-GGUF',
            path='Meta-Llama-3-8B.Q8_0.gguf',
        ),
    )
