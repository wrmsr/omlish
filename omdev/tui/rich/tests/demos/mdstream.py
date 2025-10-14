import os.path
import time

from ...markdown2 import IncrementalMarkdownRenderer


def _main() -> None:
    with open(os.path.join(os.path.dirname(__file__), '../../../apps/markdown/tests/sample.md')) as f:
        src = f.read()

    from ...markdown2 import configure_markdown_parser
    from .....markdown.tokens import token_repr, flatten_tokens
    print('\n'.join(map(token_repr, flatten_tokens(configure_markdown_parser().parse(src)))) + '\n')

    with IncrementalMarkdownRenderer() as ir:
        for c in src:
            ir.feed(c)
            time.sleep(.002)


if __name__ == '__main__':
    _main()
