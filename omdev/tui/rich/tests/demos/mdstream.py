import argparse
import os.path
import time

from ... import markdown2


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('-i', '--incremental', action='store_true')
    args = parser.parse_args()

    if (fp := args.file) is None:
        fp = os.path.join(os.path.dirname(__file__), '../../../apps/markdown/tests/sample.md')
    with open(fp) as f:
        src = f.read()

    # from ...markdown2 import configure_markdown_parser
    # from .....markdown.tokens import token_repr, flatten_tokens
    # print('\n'.join(map(token_repr, flatten_tokens(configure_markdown_parser().parse(src)))) + '\n')

    ls: markdown2.MarkdownLiveStream
    if args.incremental:
        ls = markdown2.IncrementalMarkdownLiveStream()
        # ls = markdown2.ClaudeIncrementalMarkdownLiveStream()
        # ls = markdown2.GptIncrementalMarkdownLiveStream()
    else:
        ls = markdown2.NaiveMarkdownLiveStream()

    with ls as ls:
        for c in src:
            ls.feed(c)
            time.sleep(.002)


if __name__ == '__main__':
    _main()
