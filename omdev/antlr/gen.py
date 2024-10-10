"""
TODO:
 - fix relpath in omlish/
 - sem-bounded parallelism
"""
import argparse
import os.path
import re
import shutil
import subprocess

from omlish import check
from omlish import lang

from ..cache import data as dcache
from .consts import ANTLR_JAR_URL
from .consts import ANTLR_RUNTIME_VENDOR


ANTLR_JAR_CACHE = dcache.UrlSpec(ANTLR_JAR_URL)


class GenPy:
    def __init__(
            self,
            dir: str,  # noqa
            *,
            out_subdir: str = '_antlr',
            runtime_import: str = ANTLR_RUNTIME_VENDOR,
    ) -> None:
        super().__init__()
        check.arg(not os.path.isabs(out_subdir) and '..' not in out_subdir)
        self._dir = dir
        self._out_subdir = out_subdir
        self._runtime_import = runtime_import
        self._out_dir = os.path.join(dir, out_subdir)

    @lang.cached_function
    def jar(self) -> str:
        return dcache.default().get(ANTLR_JAR_CACHE)

    def process_g4(self, g4_file: str) -> None:
        subprocess.check_call([
            'java',
            '-jar', self.jar(),
            '-Dlanguage=Python3',
            '-visitor',
            '-o', self._out_subdir,
            g4_file,
        ], cwd=self._dir)

    def process_py(self, py_file: str) -> None:
        ap = os.path.join(self._out_dir, py_file)
        with open(ap) as f:
            in_lines = list(f)

        out_lines = [
            '# type: ignore\n',
            '# ruff: noqa\n',
            '# flake8: noqa\n',
        ]
        for l in in_lines:
            l = re.sub(r'^(from antlr4)(.*)', rf'from {self._runtime_import}\2', l)
            out_lines.append(l)

        with open(ap, 'w') as f:
            f.write(''.join(out_lines))

    def run(self) -> None:
        if os.path.exists(self._out_dir):
            shutil.rmtree(self._out_dir)
        os.mkdir(self._out_dir)
        with open(os.path.join(self._out_dir, '__init__.py'), 'w'):
            pass

        for f in os.listdir(self._dir):
            fp = os.path.join(self._dir, f)
            if not os.path.isfile(fp):
                continue
            if f.endswith('.g4'):
                self.process_g4(f)

        for f in list(os.listdir(self._out_dir)):
            fp = os.path.join(self._out_dir, f)
            if not os.path.isfile(fp):
                continue
            if f.split('.')[-1] in ('interp', 'tokens'):
                os.unlink(fp)
            elif f != '__init__.py' and f.endswith('.py'):
                self.process_py(f)


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('roots', nargs='*')
    args = parser.parse_args()

    base_dir = os.getcwd()
    if not os.path.isfile(os.path.join(base_dir, 'pyproject.toml')):
        raise RuntimeError('Must run from project root')

    for root_dir in args.roots:
        print(f'Processing {root_dir}')
        GenPy(
            root_dir,
        ).run()


if __name__ == '__main__':
    _main()
