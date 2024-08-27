"""
TODO:
 - ext scanning
 - __revision__
 - entry_points

https://setuptools.pypa.io/en/latest/references/keywords.html
https://packaging.python.org/en/latest/specifications/pyproject-toml

How to build a C extension in keeping with PEP 517, i.e. with pyproject.toml instead of setup.py?
https://stackoverflow.com/a/66479252

https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py

https://pip.pypa.io/en/stable/cli/pip_install/#vcs-support
vcs+protocol://repo_url/#egg=pkg&subdirectory=pkg_dir
'git+https://github.com/wrmsr/omlish@master#subdirectory=.pip/omlish'
"""
# ruff: noqa: UP006 UP007
import dataclasses as dc
import importlib
import os.path
import shutil
import subprocess
import sys
import types
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.logs import log

from ..toml.writer import TomlWriter


class PyprojectPackageGenerator:
    def __init__(
            self,
            dir_name: str,
            build_root: str,
    ) -> None:
        super().__init__()
        self._dir_name = dir_name
        self._build_root = build_root

    #

    @cached_nullary
    def about(self) -> types.ModuleType:
        return importlib.import_module(f'{self._dir_name}.__about__')

    @cached_nullary
    def project_cls(self) -> type:
        return self.about().Project

    @cached_nullary
    def setuptools_cls(self) -> type:
        return self.about().Setuptools

    #

    @cached_nullary
    def _build_dir(self) -> str:
        build_dir: str = os.path.join(self._build_root, self._dir_name)
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        os.makedirs(build_dir)
        return build_dir

    #

    def _write_git_ignore(self) -> None:
        git_ignore = [
            '/*.egg-info/',
            '/dist',
        ]
        with open(os.path.join(self._build_dir(), '.gitignore'), 'w') as f:
            f.write('\n'.join(git_ignore))

    #

    def _symlink_source_dir(self) -> None:
        os.symlink(
            os.path.relpath(self._dir_name, self._build_dir()),
            os.path.join(self._build_dir(), self._dir_name),
        )

    #

    @dc.dataclass(frozen=True)
    class FileContents:
        pyproject_dct: ta.Mapping[str, ta.Any]
        manifest_in: ta.Optional[ta.Sequence[str]]

    @staticmethod
    def _build_cls_dct(cls: type) -> ta.Dict[str, ta.Any]:  # noqa
        dct = {}
        for b in reversed(cls.__mro__):
            for k, v in b.__dict__.items():
                if k.startswith('_'):
                    continue
                dct[k] = v
        return dct

    @staticmethod
    def _move_dict_key(
            sd: ta.Dict[str, ta.Any],
            sk: str,
            dd: ta.Dict[str, ta.Any],
            dk: str,
    ) -> None:
        if sk in sd:
            dd[dk] = sd.pop(sk)

    @cached_nullary
    def file_contents(self) -> FileContents:
        pyp_dct = {}

        #

        pyp_dct['build-system'] = {
            'requires': ['setuptools'],
            'build-backend': 'setuptools.build_meta',
        }

        prj = self._build_cls_dct(self.project_cls())
        pyp_dct['project'] = prj

        self._move_dict_key(prj, 'optional_dependencies', pyp_dct, extrask := 'project.optional-dependencies')
        if (extras := pyp_dct.get(extrask)):
            pyp_dct[extrask] = {
                'all': [
                    e
                    for lst in extras.values()
                    for e in lst
                ],
                **extras,
            }

        #

        st = self._build_cls_dct(self.setuptools_cls())
        pyp_dct['tool.setuptools'] = st

        self._move_dict_key(st, 'find_packages', pyp_dct, 'tool.setuptools.packages.find')

        mani_in = st.pop('manifest_in', None)

        #

        return self.FileContents(
            pyp_dct,
            mani_in,
        )

    def _write_file_contents(self) -> None:
        fc = self.file_contents()

        with open(os.path.join(self._build_dir(), 'pyproject.toml'), 'w') as f:
            TomlWriter(f).write_root(fc.pyproject_dct)

        if fc.manifest_in:
            with open(os.path.join(self._build_dir(), 'MANIFEST.in'), 'w') as f:
                f.write('\n'.join(fc.manifest_in))  # noqa

    #

    _STANDARD_FILES: ta.Sequence[str] = [
        'LICENSE',
        'README.rst',
    ]

    def _symlink_standard_files(self) -> None:
        for fn in self._STANDARD_FILES:
            if os.path.exists(fn):
                os.symlink(os.path.relpath(fn, self._build_dir()), os.path.join(self._build_dir(), fn))

    #

    def _run_build(
            self,
            build_output_dir: ta.Optional[str] = None,
    ) -> None:
        subprocess.check_call(
            [
                sys.executable,
                '-m',
                'build',
            ],
            cwd=self._build_dir(),
        )

        if build_output_dir is not None:
            dist_dir = os.path.join(self._build_dir(), 'dist')
            for fn in os.listdir(dist_dir):
                shutil.copyfile(os.path.join(dist_dir, fn), os.path.join(build_output_dir, fn))

    #

    def gen(
            self,
            *,
            run_build: bool = False,
            build_output_dir: ta.Optional[str] = None,
    ) -> str:
        log.info('Generating pyproject package: %s -> %s', self._dir_name, self._build_root)

        self._build_dir()
        self._write_git_ignore()
        self._symlink_source_dir()
        self._write_file_contents()
        self._symlink_standard_files()

        if run_build:
            self._run_build(build_output_dir)

        return self._build_dir()
