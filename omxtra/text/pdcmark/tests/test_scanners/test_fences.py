from pdcmark.scanning.fences import is_fence_close
from pdcmark.scanning.fences import scan_fence_open


def test_basic_backtick_open():
    m = scan_fence_open('```')
    assert m is not None
    assert m.fence_char == '`'
    assert m.fence_length == 3
    assert m.info == ''


def test_basic_tilde_open():
    m = scan_fence_open('~~~~')
    assert m is not None and m.fence_char == '~' and m.fence_length == 4


def test_open_with_info():
    m = scan_fence_open('```python')
    assert m is not None and m.info == 'python'


def test_open_strips_info_whitespace():
    m = scan_fence_open('```   python   ')
    assert m is not None and m.info == 'python'


def test_backtick_info_cannot_contain_backtick():
    assert scan_fence_open('```fo`o') is None


def test_tilde_info_can_contain_backtick():
    m = scan_fence_open('~~~ fo`o ')
    assert m is not None and m.info == 'fo`o'


def test_under_three_no():
    assert scan_fence_open('``') is None
    assert scan_fence_open('~~') is None


def test_indent_up_to_3():
    m = scan_fence_open('   ```')
    assert m is not None and m.indent == 3


def test_four_space_indent_no():
    assert scan_fence_open('    ```') is None


def test_close_matches_same_char_and_length():
    assert is_fence_close('```', '`', 3)
    assert is_fence_close('````', '`', 3)
    assert not is_fence_close('``', '`', 3)


def test_close_wrong_char_no():
    assert not is_fence_close('~~~', '`', 3)


def test_close_allows_indent_and_trailing_ws():
    assert is_fence_close('   ```   ', '`', 3)


def test_close_no_info_allowed():
    assert not is_fence_close('``` python', '`', 3)


def test_close_four_indent_no():
    assert not is_fence_close('    ```', '`', 3)
