"""
https://github.com/a2aproject/A2A
"""
import os.path

from omdev.cache import data as dcache


##


A2A_SPEC_DATA = dcache.GitSpec(
    'https://github.com/a2aproject/A2A',
    rev='c1169f45728ae5bf98d8ab0ab06e187f94002f15',
    subtrees=[
        A2A_SPEC_PATH := 'specification/a2a.proto',
    ],
)


def _main() -> None:
    spec_dir = dcache.default().get(A2A_SPEC_DATA)

    with open(os.path.join(spec_dir, A2A_SPEC_PATH)) as f:
        spec_src = f.read()

    print(spec_src)

    from omlish import check
    from omlish.text import abnf
    from omxtra.specs.proto.abnf import proto3_grammar

    parsed = check.not_none(proto3_grammar().parse(spec_src))
    parsed = abnf.only_match_rules(parsed)

    print(parsed)


if __name__ == '__main__':
    _main()
