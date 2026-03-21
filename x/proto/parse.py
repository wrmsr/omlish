import os.path

from omlish.text import abnf


def _main() -> None:
    with open(os.path.join(os.path.dirname(__file__), 'proto3.abnf')) as f:
        gram_src = f.read()

    gram = abnf.parse_grammar(gram_src, root='proto-file')

    with open(os.path.join(os.path.dirname(__file__), 'addressbook.proto')) as f:
        addressbook_src = f.read()

    addressbook = gram.parse(addressbook_src)

    print(addressbook)


if __name__ == '__main__':
    _main()
