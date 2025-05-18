import os.path

import pytest

from ...core import GrammarRule


# fuzz test data generated using abnfgen <http://www.quut.com/abnfgen/>.
FUZZ_DIR = os.path.dirname(__file__)


def load_fuzz_test_data(dirname: str):
    test_data: list[str] = []
    fd = os.path.join(FUZZ_DIR, dirname)
    for filename in os.listdir(fd):
        with open(os.path.join(fd, filename), 'rb') as f:
            test_data.append(f.read().decode('utf-8'))

    return test_data


@pytest.mark.parametrize('src', load_fuzz_test_data('char-val'))
def test_char_val(src):
    node, _ = GrammarRule('char-val').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', load_fuzz_test_data('num-val'))
def test_num_val(src):
    node, _ = GrammarRule('num-val').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', load_fuzz_test_data('repeat'))
def test_repeat(src):
    node, _ = GrammarRule('repeat').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', load_fuzz_test_data('comment'))
def test_comment(src):
    node, _ = GrammarRule('comment').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [
    """;foo\r\n""",
    """\r\n""",
])
def test_c_nl(src):
    node, _ = GrammarRule('c-nl').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', load_fuzz_test_data('c-wsp'))
def test_c_wsp(src):
    node, _ = GrammarRule('c-wsp').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', load_fuzz_test_data('rule'))
def test_rule(src):
    node, _ = GrammarRule('rule').parse(src, 0)
    assert node and node.value == src
