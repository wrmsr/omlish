import os.path

from omlish import check
import tokenize_rt as tr


def _main() -> None:
    mod_path = 'x/antlr/_vendor/antlr4'
    check.state(os.path.isdir(mod_path))
    for dp, dns, fns in os.walk(mod_path):
        print((dp, dns, fns))


if __name__ == '__main__':
    _main()
