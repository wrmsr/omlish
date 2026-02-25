from ..decode import ImmediateBytesReader
from ..decode import YamlDecoder


def test_decode():
    s = """\
%YAML 1.2
---
a: 1
b: c
"""

    d = YamlDecoder(ImmediateBytesReader(s.encode()))
    v = d.decode()
    print(v)
