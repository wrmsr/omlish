from ...scanning.lists import scan_list_marker
from ...scanning.lists import scan_task_list_marker


def test_bullets():
    for c in '-+*':
        m = scan_list_marker(c + ' foo')
        assert m is not None and m.char == c and not m.is_ordered and m.marker_width == 1


def test_bullet_followed_by_eol():
    m = scan_list_marker('-')
    assert m is not None


def test_bullet_followed_by_alpha_not_marker():
    assert scan_list_marker('-foo') is None


def test_ordered_dot():
    m = scan_list_marker('1. item')
    assert m is not None
    assert m.is_ordered and m.start == 1 and m.char == '.' and m.marker_width == 2


def test_ordered_paren():
    m = scan_list_marker('42) item')
    assert m.is_ordered and m.start == 42 and m.char == ')'  # type: ignore


def test_ordered_max_digits():
    assert scan_list_marker('1234567890. x') is None  # 10 digits — over the limit
    m = scan_list_marker('123456789. x')              # 9 digits — ok
    assert m is not None and m.start == 123456789


def test_ordered_at_eol():
    assert scan_list_marker('1.') is not None
    assert scan_list_marker('1.foo') is None


def test_non_marker():
    assert scan_list_marker('foo') is None
    assert scan_list_marker('') is None


def test_task_list_unchecked():
    m = scan_task_list_marker('[ ] thing')
    assert m is not None and not m.checked


def test_task_list_checked():
    m = scan_task_list_marker('[x] thing')
    assert m is not None and m.checked
    m = scan_task_list_marker('[X] thing')
    assert m is not None and m.checked


def test_task_list_must_be_followed_by_ws():
    assert scan_task_list_marker('[ ]foo') is None
    assert scan_task_list_marker('[ ]') is not None


def test_task_list_bad_box():
    assert scan_task_list_marker('[y] thing') is None
    assert scan_task_list_marker('[  ] thing') is None
