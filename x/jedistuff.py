"""
NOTE:
 - does not support match statement, but handles it gracefully enough for non-local indexing
  - https://github.com/davidhalter/parso/issues/138

TODO:
 - executing? asttokens?
"""
import os.path
import sys

import jedi.api.environment
import jedi.inference.compiled.subprocess

from omlish import check
from omlish import lang

from .inspectstuff import findsource


IGNORED_JEDI_EXCEPTIONS: tuple[type[BaseException], ...] = (
    # Issue #9: bad syntax causes completions() to fail in jedi.
    # https://github.com/jonathanslenders/python-prompt-toolkit/issues/9
    TypeError,

    # Issue #43: UnicodeDecodeError on OpenBSD
    # https://github.com/jonathanslenders/python-prompt-toolkit/issues/43
    UnicodeDecodeError,

    # Jedi issue #513: https://github.com/davidhalter/jedi/issues/513
    AttributeError,

    # Jedi issue: "ValueError: invalid \x escape"
    ValueError,

    # Jedi issue: "KeyError: 'a_lambda'."
    # https://github.com/jonathanslenders/ptpython/issues/89
    KeyError,

    # Jedi issue: "IOError: No such file or directory."
    # https://github.com/jonathanslenders/ptpython/issues/71
    IOError,
)


class _SubprocessHackedEnvironment(jedi.api.environment.Environment):
    def __init__(self, *args, **kwargs):
        self.__subprocess = None
        super().__init__(*args, **kwargs)

    @property
    def _subprocess(self):
        return self.__subprocess

    @_subprocess.setter
    def _subprocess(self, value):
        value = check.isinstance(value, jedi.inference.compiled.subprocess.CompiledSubprocess)
        self.__subprocess = value


def _main() -> None:
    cls = lang.Final
    cls_src = findsource(cls)
    check.state(cls_src.file_lines[cls_src.line] == 'class Final(Abstract):\n')
    file_src = ''.join(cls_src.file_lines)

    column = 13

    try:
        # script = jedi.Interpreter(
        #     file_src,
        #     path=cls_src.file,
        #     namespaces=[locals(), globals()],
        # )

        env_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..'))

        env = _SubprocessHackedEnvironment(
            os.path.join(env_path, 'bin', 'python'),
        )

        project = jedi.Project(
            os.getcwd(),
            environment_path=env_path,
            sys_path=list(sys.path),
        )

        script = jedi.Script(
            file_src,
            path=cls_src.file,
            project=project,
            environment=env,
        )

    except Exception as e:  # noqa
        return

    if not script:
        return

    try:
        infers = script.infer(
            line=cls_src.line + 1,
            column=column,
        )
    except IGNORED_JEDI_EXCEPTIONS as e:  # noqa
        return

    for i in infers:
        print(i)


if __name__ == '__main__':
    _main()
