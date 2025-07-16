import os.path

from ..rendering import LsLinesRenderer
from ..running import LsRunner


def test_ls():
    root_dir = os.path.join(os.path.dirname(__file__), 'root')

    root = LsRunner().run(root_dir)
    lines = LsLinesRenderer().render(root)
    print('\n'.join(lines.lines))
