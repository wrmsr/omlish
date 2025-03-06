from ..mangle import StringMangler


def test_mangle() -> None:
    mangler = StringMangler.of('_', '/')

    test_cases = {
        'foo/bar': 'foo_1bar',
        'foo_bar': 'foo_0bar',
        'foo/bar_baz': 'foo_1bar_0baz',
        '_leading': '_0leading',
        'trailing_': 'trailing_0',
        'nested/foo/bar_baz': 'nested_1foo_1bar_0baz',
        '/rooted': '_1rooted',
        'double//slash': 'double_1_1slash',
        'double__underscore': 'double_0_0underscore',
        'mixed_/_test': 'mixed_0_1_0test',
    }

    for original, expected in test_cases.items():
        encoded = mangler.mangle(original)
        decoded = mangler.unmangle(encoded)
        assert encoded == expected
        assert decoded == original
