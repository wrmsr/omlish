import os.path
import re
import shutil
import subprocess

from omlish import lang

from ..cache import data as dcache
from .consts import ANTLR_JAR_URL


ANTLR_JAR_CACHE = dcache.UrlSpec(ANTLR_JAR_URL)


class GenPy:
    def __init__(
            self,
            out_dir: str,
            *,
            runtime_import: str = 'omlish.antlr._runtime',
    ) -> None:
        super().__init__()
        self._out_dir = out_dir
        self._runtime_import = runtime_import

    @lang.cached_function
    def jar(self) -> str:
        return dcache.default().get(ANTLR_JAR_CACHE)

    def process_g4(self, g4_file: str) -> None:
        subprocess.check_call([
            'java',
            '-jar', self.jar(),
            '-Dlanguage=Python3',
            '-visitor',
            '-o', self._out_dir,
            g4_file,
        ])

    def process_py(self, py_file: str) -> None:
        with open(py_file) as f:
            in_lines = list(f)

        out_lines = [
            '# type: ignore\n',
            '# ruff: noqa\n',
            '# flake8: noqa\n',
        ]
        for l in in_lines:
            l = re.sub(r'^(from antlr4)(.*)', rf'from {self._runtime_import}\2', l)
            out_lines.append(l)

        with open(py_file, 'w') as f:
            f.write(''.join(out_lines))


def _main() -> None:
    base_dir = os.path.dirname(__file__)

    out_dir = os.path.join(base_dir, 'tests', '_antlr')
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)
    with open(os.path.join(out_dir, '__init__.py'), 'w'):
        pass

    gp = GenPy(
        out_dir,
    )

    for f in os.listdir(g4_dir := os.path.join(base_dir, 'tests')):
        if f.endswith('.g4'):
            gp.process_g4(os.path.join(g4_dir, f))

    for f in list(os.listdir(out_dir)):
        fp = os.path.join(out_dir, f)
        if f.split('.')[-1] in ('interp', 'tokens'):
            os.unlink(fp)
        elif f != '__init__.py' and f.endswith('.py'):
            gp.process_py(fp)


if __name__ == '__main__':
    _main()
