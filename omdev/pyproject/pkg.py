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
import abc
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
from ..tools.revisions import GitRevisionAdder


#


class BasePyprojectPackageGenerator(abc.ABC):  # noqa
    def __init__(
            self,
            dir_name: str,
            pkgs_root: str,
    ) -> None:
        super().__init__()
        self._dir_name = dir_name
        self._pkgs_root = pkgs_root

    #

    @cached_nullary
    def about(self) -> types.ModuleType:
        return importlib.import_module(f'{self._dir_name}.__about__')

    #

    @cached_nullary
    def _pkg_dir(self) -> str:
        pkg_dir: str = os.path.join(self._pkgs_root, self._dir_name)
        if os.path.isdir(pkg_dir):
            shutil.rmtree(pkg_dir)
        os.makedirs(pkg_dir)
        return pkg_dir

    #

    _GIT_IGNORE: ta.Sequence[str] = [
        '/*.egg-info/',
        '/dist',
    ]

    def _write_git_ignore(self) -> None:
        with open(os.path.join(self._pkg_dir(), '.gitignore'), 'w') as f:
            f.write('\n'.join(self._GIT_IGNORE))

    #

    def _symlink_source_dir(self) -> None:
        os.symlink(
            os.path.relpath(self._dir_name, self._pkg_dir()),
            os.path.join(self._pkg_dir(), self._dir_name),
        )

    #

    @cached_nullary
    def project_cls(self) -> type:
        return self.about().Project

    @cached_nullary
    def setuptools_cls(self) -> type:
        return self.about().Setuptools

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

    @dc.dataclass(frozen=True)
    class Specs:
        pyproject: ta.Dict[str, ta.Any]
        setuptools: ta.Dict[str, ta.Any]

    def build_specs(self) -> Specs:
        return self.Specs(
            self._build_cls_dct(self.project_cls()),
            self._build_cls_dct(self.setuptools_cls()),
        )

    #

    _STANDARD_FILES: ta.Sequence[str] = [
        'LICENSE',
        'README.rst',
    ]

    def _symlink_standard_files(self) -> None:
        for fn in self._STANDARD_FILES:
            if os.path.exists(fn):
                os.symlink(os.path.relpath(fn, self._pkg_dir()), os.path.join(self._pkg_dir(), fn))

    #

    @dc.dataclass(frozen=True)
    class GenOpts:
        run_build: bool = False
        build_output_dir: ta.Optional[str] = None
        add_revision: bool = False

    @abc.abstractmethod
    def gen(self, opts: GenOpts = GenOpts()) -> str:
        raise NotImplementedError


#


class PyprojectPackageGenerator(BasePyprojectPackageGenerator):

    #

    @dc.dataclass(frozen=True)
    class FileContents:
        pyproject_dct: ta.Mapping[str, ta.Any]
        manifest_in: ta.Optional[ta.Sequence[str]]

    @cached_nullary
    def file_contents(self) -> FileContents:
        specs = self.build_specs()

        #

        pyp_dct = {}

        pyp_dct['build-system'] = {
            'requires': ['setuptools'],
            'build-backend': 'setuptools.build_meta',
        }

        prj = specs.pyproject
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

        st = specs.setuptools
        pyp_dct['tool.setuptools'] = st

        st.pop('cexts', None)

        self._move_dict_key(st, 'find_packages', pyp_dct, 'tool.setuptools.packages.find')

        mani_in = st.pop('manifest_in', None)

        #

        return self.FileContents(
            pyp_dct,
            mani_in,
        )

    def _write_file_contents(self) -> None:
        fc = self.file_contents()

        with open(os.path.join(self._pkg_dir(), 'pyproject.toml'), 'w') as f:
            TomlWriter(f).write_root(fc.pyproject_dct)

        if fc.manifest_in:
            with open(os.path.join(self._pkg_dir(), 'MANIFEST.in'), 'w') as f:
                f.write('\n'.join(fc.manifest_in))  # noqa

    #

    def _run_build(
            self,
            build_output_dir: ta.Optional[str] = None,
            *,
            add_revision: bool = False,
    ) -> None:
        subprocess.check_call(
            [
                sys.executable,
                '-m',
                'build',
            ],
            cwd=self._pkg_dir(),
        )

        dist_dir = os.path.join(self._pkg_dir(), 'dist')

        if add_revision:
            GitRevisionAdder().add_to(dist_dir)

        if build_output_dir is not None:
            for fn in os.listdir(dist_dir):
                shutil.copyfile(os.path.join(dist_dir, fn), os.path.join(build_output_dir, fn))

    #

    def gen(self, opts: BasePyprojectPackageGenerator.GenOpts = BasePyprojectPackageGenerator.GenOpts()) -> str:
        log.info('Generating pyproject package: %s -> %s', self._dir_name, self._pkgs_root)

        self._pkg_dir()
        self._write_git_ignore()
        self._symlink_source_dir()
        self._write_file_contents()
        self._symlink_standard_files()

        if opts.run_build:
            self._run_build(
                opts.build_output_dir,
                add_revision=opts.add_revision,
            )

        return self._pkg_dir()


class _PyprojectCextPackageGenerator(BasePyprojectPackageGenerator):

    def gen(self, opts: BasePyprojectPackageGenerator.GenOpts = BasePyprojectPackageGenerator.GenOpts()) -> str:
        log.info('Generating pyproject cext package: %s -> %s', self._dir_name, self._pkgs_root)

        raise NotImplementedError
