# ruff: noqa: UP006 UP007
# @omlish-lite
"""
Notes:
 - still racy as to if it's a different actual process as initial check, just with same pid, but due to 'identity' /
   semantic meaning of the named pidfile the processes are considered equivalent

Strategies:
 - linux
  - get pid of owner (lslocks or F_GETLK)
  - open pidfd to owner pid
  - re-check pid of owner
 - darwin
  - get pids of referrers (lsof)
  - read pid from file
  - ensure pid is in referrers
  - optionally loop
  - ? setup pid death watcher? still a race
"""
import abc
import contextlib
import os.path
import shutil
import sys
import time
import typing as ta

from ...diag.lslocks import LslocksCommand
from ...diag.lsof import LsofCommand
from ...lite.check import check
from ...lite.timeouts import Timeout
from ...lite.timeouts import TimeoutLike
from ...subprocesses.sync import subprocesses  # noqa
from .pidfile import Pidfile


##


class PidfilePinner(abc.ABC):
    def __init__(
            self,
            *,
            sleep_s: float = .1,
    ) -> None:
        super().__init__()

        self._sleep_s = sleep_s

    @classmethod
    @abc.abstractmethod
    def is_available(cls) -> bool:
        raise NotImplementedError

    class NoOwnerError(Exception):
        pass

    @abc.abstractmethod
    def _pin_pidfile_owner(self, pidfile: Pidfile, timeout: Timeout) -> ta.ContextManager[int]:
        raise NotImplementedError

    @contextlib.contextmanager
    def pin_pidfile_owner(
            self,
            path: str,
            *,
            timeout: ta.Optional[TimeoutLike] = None,
            inheritable: bool = False,  # Present to match Pidfile kwargs for convenience, but enforced to be False.
            **kwargs: ta.Any,
    ) -> ta.Iterator[int]:
        check.arg(not inheritable)

        timeout = Timeout.of(timeout)

        if not os.path.isfile(path):
            raise self.NoOwnerError

        with Pidfile(
                path,
                inheritable=False,
                **kwargs,
        ) as pf:
            try:
                with self._pin_pidfile_owner(pf, timeout) as pid:
                    yield pid

            except Pidfile.NotLockedError:
                raise self.NoOwnerError from None

    @classmethod
    def default_impl(cls) -> ta.Type['PidfilePinner']:
        for impl in [
            LslocksPidfdPidfilePinner,
            LsofPidfilePinner,
        ]:
            if impl.is_available():
                return impl
        return UnverifiedPidfilePinner


##


class UnverifiedPidfilePinner(PidfilePinner):
    @classmethod
    def is_available(cls) -> bool:
        return True

    @contextlib.contextmanager
    def _pin_pidfile_owner(self, pidfile: Pidfile, timeout: Timeout) -> ta.Iterator[int]:
        while (pid := pidfile.read()) is None:
            time.sleep(self._sleep_s)
            timeout()

        yield pid


##


class LsofPidfilePinner(PidfilePinner):
    """
    Fundamentally wrong, but still better than nothing. Simply reads the file contents and ensures a valid contained pid
    has the file open via `lsof`.
    """

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which('lsof') is not None

    def _try_read_and_verify(self, pf: Pidfile, timeout: Timeout) -> ta.Optional[int]:
        if (initial_pid := pf.read()) is None:
            return None

        lsof_output = LsofCommand(
            # pid=initial_pid,
            file=os.path.abspath(pf.path),
        ).run(
            timeout=timeout,
        )

        lsof_pids: ta.Set[int] = set()
        for li in lsof_output:
            if li.pid is None:
                continue
            try:
                li_pid = int(li.pid)
            except ValueError:
                continue
            lsof_pids.add(li_pid)

        if initial_pid not in lsof_pids:
            return None

        if (reread_pid := pf.read()) is None or reread_pid != initial_pid:
            return None

        return reread_pid

    @contextlib.contextmanager
    def _pin_pidfile_owner(self, pidfile: Pidfile, timeout: Timeout) -> ta.Iterator[int]:
        while (pid := self._try_read_and_verify(pidfile, timeout)) is None:
            time.sleep(self._sleep_s)
            timeout()

        yield pid


##


class LslocksPidfdPidfilePinner(PidfilePinner):
    """
    Finds the locking pid via `lslocks`, opens a pidfd, then re-runs `lslocks` and rechecks the locking pid is the same.
    """

    @classmethod
    def is_available(cls) -> bool:
        return sys.platform == 'linux' and shutil.which('lslocks') is not None

    def _read_locking_pid(self, path: str, timeout: Timeout) -> int:
        lsl_output = LslocksCommand().run(timeout=timeout)

        lsl_pids = {
            li.pid
            for li in lsl_output
            if li.path == path
            and li.type == 'FLOCK'
        }
        if not lsl_pids:
            raise self.NoOwnerError
        if len(lsl_pids) != 1:
            raise RuntimeError(f'Multiple locks on file: {path}')

        [pid] = lsl_pids
        return pid

    class _Result(ta.NamedTuple):
        pid: int
        pidfd: int

    def _try_read_and_verify(
            self,
            pidfile: Pidfile,
            timeout: Timeout,
    ) -> ta.Optional[_Result]:
        path = os.path.abspath(pidfile.path)
        initial_pid = self._read_locking_pid(path, timeout)

        try:
            pidfd = os.open(f'/proc/{initial_pid}', os.O_RDONLY)
        except FileNotFoundError:
            raise self.NoOwnerError from None

        try:
            reread_pid = self._read_locking_pid(path, timeout)
            if reread_pid != initial_pid:
                os.close(pidfd)
                return None

            return self._Result(initial_pid, pidfd)

        except BaseException:
            os.close(pidfd)
            raise

    @contextlib.contextmanager
    def _pin_pidfile_owner(
            self,
            pidfile: Pidfile,
            timeout: Timeout,
    ) -> ta.Iterator[int]:
        while (res := self._try_read_and_verify(pidfile, timeout)) is None:
            time.sleep(self._sleep_s)
            timeout()

        try:
            yield res.pid
        finally:
            os.close(res.pidfd)


##


if __name__ == '__main__':
    def _main() -> None:
        argparse = __import__('argparse')
        parser = argparse.ArgumentParser()
        parser.add_argument('file')
        args = parser.parse_args()

        with PidfilePinner.default_impl()().pin_pidfile_owner(
                args.file,
                timeout=5.,
        ) as pid:
            print(pid)

    _main()
