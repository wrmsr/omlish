import pytest

from omlish.testing import pytest as ptu

from ..lm import load_model


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('mlx_lm')
def test_tools():
    loaded = load_model('mlx-community/Qwen2.5-0.5B-4bit')  # noqa
