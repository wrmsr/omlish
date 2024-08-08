import itertools
import os.path
import pprint

import tokenize_rt


def _main() -> None:
    root_dir = os.path.dirname(__file__)

    for src_file in [
        'demo/demo.py',
        'demo/stdlib.py',
    ]:
        print(src_file)

        with open(os.path.join(root_dir, src_file)) as f:
            src = f.read()

        print(src)

        toks = tokenize_rt.src_to_tokens(src)
        pprint.pprint(toks)

        tok_lines = [list(it) for g, it in itertools.groupby(toks, lambda t: t.line)]
        pprint.pprint(tok_lines)

        src2 = tokenize_rt.tokens_to_src(toks)
        print(src2)


if __name__ == '__main__':
    _main()
