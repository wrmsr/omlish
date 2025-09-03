# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import io
import os.path
import sys
import typing as ta

from ..lite.abstract import Abstract
from ..lite.cached import cached_nullary
from ..lite.check import check
from ..os.paths import is_path_in_dir


##


class FnBuilder(Abstract):
    @abc.abstractmethod
    def build_fn(
            self,
            name: str,
            src: str,
            ns: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Callable:
        ...


#


class SimpleFnBuilder(FnBuilder):
    def build_fn(
            self,
            name: str,
            src: str,
            ns: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Callable:
        ns = dict(ns or {})
        exec(src, ns)
        return ns[name]


build_fn = SimpleFnBuilder().build_fn


#


class DebugFnBuilder(FnBuilder):
    def __init__(
            self,
            *,
            mod_name_prefix: ta.Optional[str] = None,
            src_dir: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        if mod_name_prefix is None:
            mod_name_prefix = f'_{self.__class__.__name__}_{id(self):x}_'
        self._mod_name_prefix = mod_name_prefix

        self._given_src_dir = src_dir

        self._num_fns = 0
        self._mod_names: ta.Set[str] = set()
        self._installed_sys_path = False

    @cached_nullary
    def _src_dir(self) -> str:
        if self._given_src_dir is not None:
            return self._given_src_dir
        else:
            import tempfile  # noqa
            return tempfile.mkdtemp(prefix=f'_{self.__class__.__name__}_{os.getpid()}__')  # noqa

    @cached_nullary
    def _install_sys_path(self) -> None:
        if (src_dir := self._src_dir()) not in sys.path:
            self._installed_sys_path = True
            sys.path.append(src_dir)

    def uninstall_sys_path(self) -> None:
        if self._installed_sys_path:
            while True:
                try:
                    sys.path.remove(self._src_dir())
                except ValueError:
                    break
            self._installed_sys_path = True

    def _gen_mod_name(
            self,
            fn_num: int,
            fn_name: str,
            *,
            suffix: ta.Optional[str] = None,
    ) -> str:
        mod_name = f'{self._mod_name_prefix}{fn_num}__{fn_name}{suffix or ""}'

        check.not_in(mod_name, self._mod_names)
        check.not_in(mod_name, sys.modules)

        self._mod_names.add(mod_name)

        return mod_name

    def _build_mod(
            self,
            mod_name: str,
            mod_src: str,
    ) -> ta.Any:
        self._install_sys_path()

        src_dir = self._src_dir()
        src_file = os.path.join(src_dir, f'{mod_name}.py')
        check.state(is_path_in_dir(src_dir, src_file))

        with open(src_file, 'w') as f:
            f.write(mod_src)

        mod = __import__(mod_name)

        check.equal(mod.__file__, src_file)

        return mod

    def build_fn(
            self,
            name: str,
            src: str,
            ns: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Callable:
        fn_num = self._num_fns
        self._num_fns += 1

        mod_name = self._gen_mod_name(fn_num, name)

        src_preamble: ta.List[str] = []

        if ns:
            ns_mod_name = self._gen_mod_name(fn_num, name, suffix='__ns')
            ns_mod = self._build_mod(ns_mod_name, '')

            for k, v in ns.items():
                setattr(ns_mod, k, v)

            src_preamble.append(f'from {ns_mod_name} import (')
            for k in sorted(ns):
                src_preamble.append(f'    {k},')
            src_preamble.append(')')

        src_sb = io.StringIO()
        if src_preamble:
            src_sb.write('\n'.join(src_preamble))
            src_sb.write('\n\n')
        src_sb.write(src)
        if not src.endswith('\n'):
            src_sb.write('\n')

        mod = self._build_mod(mod_name, src_sb.getvalue())

        fn = mod.__dict__[name]
        return fn
