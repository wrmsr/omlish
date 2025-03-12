"""
TODO:
 - ext scanning
 - __revision__
 - entry_points

** NOTE **
setuptools now (2024/09/02) has experimental support for extensions in pure pyproject.toml - but we still want a
separate '-cext' package
  https://setuptools.pypa.io/en/latest/userguide/ext_modules.html
  https://github.com/pypa/setuptools/commit/1a9d87308dc0d8aabeaae0dce989b35dfb7699f0#diff-61d113525e9cc93565799a4bb8b34a68e2945b8a3f7d90c81380614a4ea39542R7-R8

--

https://setuptools.pypa.io/en/latest/references/keywords.html
https://packaging.python.org/en/latest/specifications/pyproject-toml

How to build a C extension in keeping with PEP 517, i.e. with pyproject.toml instead of setup.py?
https://stackoverflow.com/a/66479252

https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py

https://pip.pypa.io/en/stable/cli/pip_install/#vcs-support
vcs+protocol://repo_url/#egg=pkg&subdirectory=pkg_dir
'git+https://github.com/wrmsr/omlish@master#subdirectory=.pip/omlish'
"""  # noqa
# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import importlib
import os.path
import shutil
import sys
import tempfile
import types
import typing as ta

from omlish.formats.toml.writer import TomlWriter
from omlish.lite.cached import cached_nullary
from omlish.lite.logs import log
from omlish.subprocesses.sync import subprocesses

from ..cexts.magic import CextMagic
from ..magic.find import find_magic_files
from ..packaging.revisions import GitRevisionAdder


#


class BasePyprojectPackageGenerator(abc.ABC):
    def __init__(
            self,
            dir_name: str,
            pkgs_root: str,
            *,
            pkg_suffix: str = '',
    ) -> None:
        super().__init__()
        self._dir_name = dir_name
        self._pkgs_root = pkgs_root
        self._pkg_suffix = pkg_suffix

    #

    @cached_nullary
    def about(self) -> types.ModuleType:
        return importlib.import_module(f'{self._dir_name}.__about__')

    #

    @cached_nullary
    def _pkg_dir(self) -> str:
        pkg_dir: str = os.path.join(self._pkgs_root, self._dir_name + self._pkg_suffix)
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

    class _PkgData(ta.NamedTuple):
        inc: ta.List[str]
        exc: ta.List[str]

    @cached_nullary
    def _collect_pkg_data(self) -> _PkgData:
        inc: ta.List[str] = []
        exc: ta.List[str] = []

        for p, ds, fs in os.walk(self._dir_name):  # noqa
            for f in fs:
                if f != '.pkgdata':
                    continue
                rp = os.path.relpath(p, self._dir_name)
                log.info('Found pkgdata %s for pkg %s', rp, self._dir_name)
                with open(os.path.join(p, f)) as fo:
                    src = fo.read()
                for l in src.splitlines():
                    if not (l := l.strip()):
                        continue
                    if l.startswith('!'):
                        exc.append(os.path.join(rp, l[1:]))
                    else:
                        inc.append(os.path.join(rp, l))

        return self._PkgData(inc, exc)

    #

    @abc.abstractmethod
    def _write_file_contents(self) -> None:
        raise NotImplementedError

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

    def children(self) -> ta.Sequence['BasePyprojectPackageGenerator']:
        return []

    #

    def gen(self) -> str:
        log.info('Generating pyproject package: %s -> %s (%s)', self._dir_name, self._pkgs_root, self._pkg_suffix)

        self._pkg_dir()
        self._write_git_ignore()
        self._symlink_source_dir()
        self._write_file_contents()
        self._symlink_standard_files()

        return self._pkg_dir()

    #

    @dc.dataclass(frozen=True)
    class BuildOpts:
        add_revision: bool = False
        test: bool = False

    def build(
            self,
            output_dir: ta.Optional[str] = None,
            opts: BuildOpts = BuildOpts(),
    ) -> None:
        subprocesses.check_call(
            sys.executable,
            '-m',
            'build',
            cwd=self._pkg_dir(),
        )

        dist_dir = os.path.join(self._pkg_dir(), 'dist')

        if opts.add_revision:
            GitRevisionAdder().add_to(dist_dir)

        if opts.test:
            for fn in os.listdir(dist_dir):
                tmp_dir = tempfile.mkdtemp()

                subprocesses.check_call(
                    sys.executable,
                    '-m', 'venv',
                    'test-install',
                    cwd=tmp_dir,
                )

                subprocesses.check_call(
                    os.path.join(tmp_dir, 'test-install', 'bin', 'python3'),
                    '-m', 'pip',
                    'install',
                    os.path.abspath(os.path.join(dist_dir, fn)),
                    cwd=tmp_dir,
                )

        if output_dir is not None:
            for fn in os.listdir(dist_dir):
                shutil.copyfile(os.path.join(dist_dir, fn), os.path.join(output_dir, fn))


#


class PyprojectPackageGenerator(BasePyprojectPackageGenerator):
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
        prj['name'] += self._pkg_suffix

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

        if (eps := prj.pop('entry_points', None)):
            pyp_dct['project.entry-points'] = {TomlWriter.Literal(f"'{k}'"): v for k, v in eps.items()}  # type: ignore  # noqa

        if (scs := prj.pop('scripts', None)):
            pyp_dct['project.scripts'] = scs

        prj.pop('cli_scripts', None)

        ##

        st = dict(specs.setuptools)
        pyp_dct['tool.setuptools'] = st

        st.pop('cexts', None)

        #

        # TODO: default
        # find_packages = {
        #     'include': [Project.name, f'{Project.name}.*'],
        #     'exclude': [*SetuptoolsBase.find_packages['exclude']],
        # }

        fp = dict(st.pop('find_packages', {}))

        pyp_dct['tool.setuptools.packages.find'] = fp

        #

        # TODO: default
        # package_data = {
        #     '*': [
        #         '*.c',
        #         '*.cc',
        #         '*.h',
        #         '.manifests.json',
        #         'LICENSE',
        #     ],
        # }

        pd = dict(st.pop('package_data', {}))
        epd = dict(st.pop('exclude_package_data', {}))

        cpd = self._collect_pkg_data()
        if cpd.inc:
            pd['*'] = [*pd.get('*', []), *sorted(set(cpd.inc))]
        if cpd.exc:
            epd['*'] = [*epd.get('*', []), *sorted(set(cpd.exc))]

        if pd:
            pyp_dct['tool.setuptools.package-data'] = pd
        if epd:
            pyp_dct['tool.setuptools.exclude-package-data'] = epd

        #

        # TODO: default
        # manifest_in = [
        #     'global-exclude **/conftest.py',
        # ]

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

    @cached_nullary
    def children(self) -> ta.Sequence[BasePyprojectPackageGenerator]:
        out: ta.List[BasePyprojectPackageGenerator] = []

        if self.build_specs().setuptools.get('cexts'):
            out.append(_PyprojectCextPackageGenerator(
                self._dir_name,
                self._pkgs_root,
                pkg_suffix='-cext',
            ))

        if self.build_specs().pyproject.get('cli_scripts'):
            out.append(_PyprojectCliPackageGenerator(
                self._dir_name,
                self._pkgs_root,
                pkg_suffix='-cli',
            ))

        return out


#


class _PyprojectCextPackageGenerator(BasePyprojectPackageGenerator):
    @cached_nullary
    def find_cext_srcs(self) -> ta.Sequence[str]:
        return sorted(find_magic_files(
            CextMagic.STYLE,
            [self._dir_name],
            keys=[CextMagic.KEY],
        ))

    #

    @dc.dataclass(frozen=True)
    class FileContents:
        pyproject_dct: ta.Mapping[str, ta.Any]
        setup_py: str

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
        prj['dependencies'] = [f'{prj["name"]} == {prj["version"]}']
        prj['name'] += self._pkg_suffix
        for k in [
            'optional_dependencies',
            'entry_points',
            'scripts',
            'cli_scripts',
        ]:
            prj.pop(k, None)

        pyp_dct['project'] = prj

        #

        st = dict(specs.setuptools)
        pyp_dct['tool.setuptools'] = st

        for k in [
            'cexts',

            'find_packages',
            'package_data',
            'manifest_in',
        ]:
            st.pop(k, None)

        pyp_dct['tool.setuptools.packages.find'] = {
            'include': [],
        }

        #

        ext_lines = []

        for ext_src in self.find_cext_srcs():
            ext_name = ext_src.rpartition('.')[0].replace(os.sep, '.')
            ext_lines.extend([
                'st.Extension(',
                f"    name='{ext_name}',",
                f"    sources=['{ext_src}'],",
                "    extra_compile_args=['-std=c++20'],",
                '),',
            ])

        src = '\n'.join([
            'import setuptools as st',
            '',
            '',
            'st.setup(',
            '    ext_modules=[',
            *['        ' + l for l in ext_lines],
            '    ]',
            ')',
            '',
        ])

        #

        return self.FileContents(
            pyp_dct,
            src,
        )

    def _write_file_contents(self) -> None:
        fc = self.file_contents()

        with open(os.path.join(self._pkg_dir(), 'pyproject.toml'), 'w') as f:
            TomlWriter(f).write_root(fc.pyproject_dct)

        with open(os.path.join(self._pkg_dir(), 'setup.py'), 'w') as f:
            f.write(fc.setup_py)


##


class _PyprojectCliPackageGenerator(BasePyprojectPackageGenerator):
    @dc.dataclass(frozen=True)
    class FileContents:
        pyproject_dct: ta.Mapping[str, ta.Any]

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
        prj['dependencies'] = [f'{prj["name"]} == {prj["version"]}']
        prj['name'] += self._pkg_suffix
        for k in [
            'optional_dependencies',
            'entry_points',
            'scripts',
        ]:
            prj.pop(k, None)

        pyp_dct['project'] = prj

        if (scs := prj.pop('cli_scripts', None)):
            pyp_dct['project.scripts'] = scs

        #

        st = dict(specs.setuptools)
        pyp_dct['tool.setuptools'] = st

        for k in [
            'cexts',

            'find_packages',
            'package_data',
            'manifest_in',
        ]:
            st.pop(k, None)

        pyp_dct['tool.setuptools.packages.find'] = {
            'include': [],
        }

        #

        return self.FileContents(
            pyp_dct,
        )

    def _write_file_contents(self) -> None:
        fc = self.file_contents()

        with open(os.path.join(self._pkg_dir(), 'pyproject.toml'), 'w') as f:
            TomlWriter(f).write_root(fc.pyproject_dct)
