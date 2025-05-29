import pytest

from ..cli import DEFAULT_MODEL
from ..generation import GenerationParams
from ..generation import generate
from ..loading import load_model


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_simple():
    loaded = load_model(DEFAULT_MODEL)  # noqa

    generated = generate(
        loaded.model,
        loaded.tokenization,
        'Silt is',
        GenerationParams(
            max_tokens=128,
        ),
    )

    print(generated)
