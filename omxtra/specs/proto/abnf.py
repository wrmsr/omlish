import os.path

from omlish import check
from omlish.text import abnf


def _main() -> None:
    with open(os.path.join(os.path.dirname(__file__), 'proto3.abnf')) as f:
        gram_src = f.read()

    gram = abnf.parse_grammar(gram_src, root='proto-file')

    with open(os.path.join(os.path.dirname(__file__), 'tests', 'examples', 'addressbook.proto')) as f:
        addressbook_src = f.read()

    addressbook = check.not_none(gram.parse(addressbook_src))
    addressbook = abnf.only_match_rules(addressbook)

    print(addressbook.render(indent=2))


if __name__ == '__main__':
    _main()
