import os.path

from omlish.text import abnf


def _main() -> None:
    with open(os.path.join(os.path.dirname(__file__), 'minisql.abnf')) as f:
        gram = abnf.parse_grammar(f.read(), root='single-stmt')

    m = gram.parse('select x from y;')
    print(m)


if __name__ == '__main__':
    _main()
