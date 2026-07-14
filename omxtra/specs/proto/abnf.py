import os.path

from omcore import check
from omcore import lang
from omcore.text import abnf


##


@lang.cached_function(lock=True)
def proto3_grammar() -> abnf.Grammar:
    with open(os.path.join(os.path.dirname(__file__), 'proto3.abnf')) as f:
        src = f.read()

    return abnf.parse_grammar(src, root='proto-file')


##


def _main() -> None:
    gram = proto3_grammar()

    with open(os.path.join(os.path.dirname(__file__), 'tests', 'examples', 'addressbook.proto')) as f:
        addressbook_src = f.read()

    addressbook = check.not_none(gram.parse(addressbook_src))
    addressbook = abnf.only_match_rules(addressbook)

    print(addressbook.render(indent=2))


if __name__ == '__main__':
    _main()
