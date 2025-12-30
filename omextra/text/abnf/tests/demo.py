import os.path

from omlish import check
from omlish import lang

from ..grammars import Channel
from ..grammars import Grammar
from ..meta import parse_grammar
from ..utils import filter_match_channels
from ..utils import fix_ws
from ..utils import only_match_rules


@lang.cached_function
def parse_demo_grammar() -> Grammar:
    with open(os.path.join(os.path.dirname(__file__), 'demo.abnf')) as f:
        gram_src = f.read()

    return parse_grammar(
        gram_src,
        root='config',
        # debug=True,
    )


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', metavar='file-name', nargs='?', default='demo2.txt')
    parser.add_argument('-x', '--max-steps', type=int)
    args = parser.parse_args()

    gram = parse_demo_grammar()

    with open(os.path.join(os.path.dirname(__file__), args.file_name)) as f:
        ast_src = f.read()

    ast_src = fix_ws(ast_src)

    m = check.not_none(gram.parse(
        ast_src,
        complete=True,
        # debug=True,
        max_steps=args.max_steps,
    ))

    print(m.render(indent=2))

    m = only_match_rules(m)

    m = filter_match_channels(
        m,
        gram,
        keep=(Channel.STRUCTURE,),
        keep_children=True,
    )

    print(m.render(indent=2))


if __name__ == '__main__':
    _main()
