import inspect
import os.path
import sys
import tempfile
import typing as ta

from omlish import cached
from omlish import check

from . import _cmdlog


##


class CmdLog:
    def __init__(
            self,
            proxied_cmds: ta.Iterable[str],
            *,
            tmp_dir: str | None = None,
            log_file: str | None = None,
            exe_name: str | None = None,
    ) -> None:
        super().__init__()

        self._proxied_cmds = {
            check.non_empty_str(c)
            for c in check.not_isinstance(proxied_cmds, str)
        }

        self._given_tmp_dir = tmp_dir
        self._given_log_file = log_file
        self._exe_name = check.non_empty_str(exe_name) if exe_name is not None else self.DEFAULT_EXE_NAME

    #

    @cached.function
    def tmp_dir(self) -> str:
        if (gtd := self._given_tmp_dir) is not None:
            return gtd
        return tempfile.mkdtemp()

    #

    DEFAULT_LOG_FILE_NAME: ta.ClassVar[str] = '_cmdlog.jsonl'

    @cached.function
    def log_file(self) -> str:
        if (glf := self._given_log_file) is not None:
            return glf
        return os.path.join(self.tmp_dir(), self.DEFAULT_LOG_FILE_NAME)

    #

    DEFAULT_EXE_NAME: ta.ClassVar[str] = '_cmdlog.py'

    @cached.function
    def exe(self) -> str:
        src = '\n'.join([
            f'#!{os.path.abspath(sys.executable)}',
            inspect.getsource(_cmdlog),
        ])

        exe = os.path.join(self.tmp_dir(), self._exe_name)

        with open(exe, 'w') as f:
            f.write(src)

        os.chmod(exe, 0o550)  # noqa

        return exe

    #

    def proxy_cmds(self) -> None:
        for p_c in self._proxied_cmds:
            os.symlink(self._exe_name, os.path.join(self.tmp_dir(), p_c))

    #

    def child_env(self) -> ta.Mapping[str, str]:
        return {
            _cmdlog.LOG_FILE_ENV_VAR: self.log_file(),
            'PATH': os.pathsep.join([self.tmp_dir(), os.environ['PATH']]),
        }
