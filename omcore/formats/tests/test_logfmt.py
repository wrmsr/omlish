from ..logfmt import logfmt_decode
from ..logfmt import logfmt_encode


def test_logfmt():
    dct = {
        'foo': 'bar',
        'a': 14,
        'baz': 'hello kitty',
        'cool%story': 'bro',
        'f': True,
        '%^asdf': True,
        'spa ce': 'qu"ote',
        'sl\\ash': 'sl\\ash qu"ote',
        'i have\na newline': 'i also\nhave\nnewlines\n\n',
    }

    line = logfmt_encode(dct)
    assert line == ' '.join([
        'foo=bar',
        'a=14',
        'baz="hello kitty"',
        'cool%story=bro',
        'f',
        '%^asdf',
        '"spa ce"="qu\\"ote"',
        'sl\\ash="sl\\\\ash qu\\"ote"',
        '"i have\\na newline"="i also\\nhave\\nnewlines\\n\\n"',
    ])

    dct2 = logfmt_decode(line)
    assert dct == dct2
