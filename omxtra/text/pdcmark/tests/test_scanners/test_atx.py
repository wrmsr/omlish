from pdcmark.scanning.atx import scan_atx_open


def _content(line, m):
    return line[m.content_start:m.content_end]


def test_basic_levels():
    for level in range(1, 7):
        m = scan_atx_open('#' * level + ' x')
        assert m is not None and m.level == level


def test_no_space_after_hashes_not_a_heading():
    assert scan_atx_open('#hashtag') is None


def test_seventh_hash_is_not_heading():
    assert scan_atx_open('####### too many') is None


def test_content_extraction():
    line = '## hello world'
    m = scan_atx_open(line)
    assert m is not None
    assert _content(line, m) == 'hello world'


def test_strips_trailing_hashes_after_space():
    line = '## hi ##'
    m = scan_atx_open(line)
    assert _content(line, m) == 'hi'


def test_no_trailing_hash_strip_without_space():
    line = '## hi##'
    m = scan_atx_open(line)
    assert _content(line, m) == 'hi##'


def test_empty_heading():
    m = scan_atx_open('#')
    assert m is not None and m.level == 1 and m.content_start == m.content_end

    m = scan_atx_open('# ')
    assert m is not None and m.content_start == m.content_end


def test_tab_after_hashes():
    line = '#\tfoo'
    m = scan_atx_open(line)
    assert m is not None
    assert _content(line, m) == 'foo'
