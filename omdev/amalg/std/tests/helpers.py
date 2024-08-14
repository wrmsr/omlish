import abc

from .. import subprocesses as su
from ..contextmanagers import attr_setting


class SubprocessPatchingTest(abc.ABC):  # noqa
    def setUp(self):  # noqa
        super().setUp()  # type: ignore

        cm = attr_setting(su, '_SUBPROCESS_SHELL_WRAP_EXECS', True)
        cm.__enter__()
        self.addCleanup(cm.__exit__, None, None, None)  # type: ignore
