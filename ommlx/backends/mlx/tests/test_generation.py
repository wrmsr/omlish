import pytest

from omlish.testing import pytest as ptu

from ..cli import DEFAULT_MODEL
from ..generation import generate
from ..loading import load_model


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
@ptu.skip.if_cant_import('mlx_lm')
def test_simple():
    loaded = load_model(DEFAULT_MODEL)  # noqa
    generated = generate(
        loaded.model,
        loaded.tokenizer,
        'Silt is',
        max_tokens=128,
    )
    print(generated)
