import os.path

from ..parsing import ParsedBackendString
from ..parsing import parse_backend_string


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
