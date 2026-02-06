"""
TODO:
 - mtime cmp
 - parallelism
"""
import os.path
import re
import shutil
import subprocess
import typing as ta

from omlish import check
from omlish import lang
from omlish.logs import all as logs
from omlish.os.paths import is_path_in_dir

from .consts import ANTLR_JAR_URL
from .consts import ANTLR_RUNTIME_VENDOR


if ta.TYPE_CHECKING:
    from omdev.cache import data as dcache
else:
    dcache = lang.proxy_import('omdev.cache.data')


log = logs.get_module_logger(globals())


##


ANTLR_JAR_CACHE = dcache.UrlSpec(ANTLR_JAR_URL)


@lang.cached_function
def get_jar_path() -> str:
    return dcache.default().get(ANTLR_JAR_CACHE)


##


def _find_dirs(*base_paths: str, filter: ta.Callable[[str], bool] = lambda _: True) -> ta.Sequence[str]:  # noqa
    return sorted(
        os.path.join(dp, dn)
        for base_path in base_paths
        for dp, dns, fns in os.walk(base_path)
        for dn in dns
        if filter(dn)
    )


def _find_files(*base_paths: str, filter: ta.Callable[[str], bool] = lambda _: True) -> ta.Sequence[str]:  # noqa
    return sorted(
        os.path.join(dp, fn)
        for base_path in base_paths
        for dp, dns, fns in os.walk(base_path)
        for fn in fns
        if filter(fn)
    )


class GenPy:
    def __init__(
            self,
            root_dirs: str,  # noqa
            *,
            out_subdir: str = '_antlr',
            runtime_import: str = ANTLR_RUNTIME_VENDOR,
            jar_path: str | None = None,
            # parallelism: int | None = None,
    ) -> None:
        super().__init__()

        check.non_empty_str(out_subdir)
        check.arg(not os.path.isabs(out_subdir) and '.' not in out_subdir and '/' not in out_subdir)

        self._root_dirs = frozenset(check.non_empty_str(rd) for rd in check.not_isinstance(root_dirs, str))
        self._out_subdir = out_subdir
        self._runtime_import = runtime_import
        self._given_jar_path = jar_path

    #

    def _rmtree(self, tgt: str) -> None:  # noqa
        if not any(is_path_in_dir(rd, tgt) for rd in self._root_dirs):
            raise RuntimeError(f'Refusing to delete {tgt!r} outside of {self._root_dirs!r}')
        shutil.rmtree(tgt)

    #

    @lang.cached_function
    def jar_path(self) -> str:
        if (gjp := self._given_jar_path) is not None:
            return gjp
        return get_jar_path()

    #

    def process_g4(self, g4_file: str) -> None:
        ap = os.path.abspath(g4_file)
        check.state(os.path.isfile(ap))

        od = os.path.join(os.path.dirname(ap), self._out_subdir)
        os.makedirs(od, exist_ok=True)

        log.info('Compiling grammar %s', g4_file)

        try:
            subprocess.check_call([
                'java',
                '-jar', self.jar_path(),
                '-Dlanguage=Python3',
                '-visitor',
                '-o', self._out_subdir,
                os.path.basename(g4_file),
            ], cwd=os.path.dirname(ap))

        except Exception:  # noqa
            log.exception('Exception in grammar %s', g4_file)
            raise

    def process_py(self, py_file: str) -> None:
        ap = os.path.abspath(py_file)
        with open(ap) as f:
            in_lines = list(f)

        pfp = py_file.split(os.sep)
        arp = ANTLR_RUNTIME_VENDOR.split('.')
        if (cpl := lang.common_prefix_len(pfp, arp)) > 0:
            pkg_depth = len(os.path.normpath(py_file).split(os.path.sep))
            antlr_imp = '.'.join([*([''] * (pkg_depth - cpl)), *arp[cpl:]])
        else:
            antlr_imp = ANTLR_RUNTIME_VENDOR

        out_lines = [
            '# type: ignore\n',
            '# ruff: noqa\n',
            '# flake8: noqa\n',
            '# @omlish-generated\n',
        ]

        for l in in_lines:
            l = re.sub(r'^(from antlr4)(.*)', rf'from {antlr_imp}\2', l)
            out_lines.append(l)

        with open(ap, 'w') as f:
            f.write(''.join(out_lines))

    def process_dir(self, dir: str) -> None:  # noqa
        log.info('Processing directory %s', dir)

        ad = os.path.join(dir, self._out_subdir)
        if os.path.exists(ad):
            self._rmtree(ad)

        for f in os.listdir(dir):
            fp = os.path.join(dir, f)
            if not os.path.isfile(fp) or not f.endswith('.g4'):
                continue

            self.process_g4(fp)

        if not os.path.exists(ad):
            return

        ip = os.path.join(ad, '__init__.py')
        check.state(not os.path.exists(ip))

        for f in list(os.listdir(ad)):
            fp = os.path.join(ad, f)
            if not os.path.isfile(fp):
                continue

            if f.split('.')[-1] in ('interp', 'tokens'):
                os.unlink(fp)

            elif f != '__init__.py' and f.endswith('.py'):
                self.process_py(fp)

        with open(ip, 'w'):
            pass

    def run(self) -> None:
        dns = _find_dirs(*self._root_dirs, filter=lambda dn: os.path.basename(dn) == '_antlr')
        for dn in dns:
            self._rmtree(dn)

        fns = _find_files(*self._root_dirs, filter=lambda fn: fn.endswith('.g4'))
        fds = {os.path.dirname(fn) for fn in fns}
        for dn in sorted(fds):
            self.process_dir(dn)
