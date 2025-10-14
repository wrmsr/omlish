import os.path

from ...markdown2 import IncrementalMarkdownRenderer


def _main() -> None:
    with open(os.path.join(os.path.dirname(__file__), '../../../apps/markdown/tests/sample.md')) as f:
        src = f.read()

    with IncrementalMarkdownRenderer() as ir:
        for c in src:
            ir.feed(c)


if __name__ == '__main__':
    _main()
