import os.path
import pprint

import tokenize_rt


def _main() -> None:
    root_dir = os.path.dirname(__file__)
    with open(os.path.join(root_dir, 'demo/demo.py')) as f:
        src = f.read()

    print(src)

    toks = tokenize_rt.src_to_tokens(src)
    pprint.pprint(toks)

    src2 = tokenize_rt.tokens_to_src(toks)
    print(src2)


if __name__ == '__main__':
    _main()
