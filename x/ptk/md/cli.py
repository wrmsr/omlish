import sys

from omdev import ptk

from .markdown import Markdown
from .styles import MARKDOWN_STYLE


##


def _main() -> None:
    with open(sys.argv[1]) as f:
        ptk.print_formatted_text(
            Markdown(f.read()),
            style=ptk.Style(MARKDOWN_STYLE),
        )


if __name__ == '__main__':
    _main()
