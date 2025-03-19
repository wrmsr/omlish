"""
NOTE:
 - does not support match statement, but handles it gracefully enough for non-local indexing
  - https://github.com/davidhalter/parso/issues/138

TODO:
 - executing? asttokens?
"""
import os.path
import shlex
import sys
import tempfile

import jedi.api.environment

from omlish import check
from omlish import lang
from omlish.diag import pydevd

from ..inspect import find_source


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


def _main() -> None:
    cls = lang.Final
    cls_src = find_source(cls)
    check.state(cls_src.file_lines[cls_src.line] == 'class Final(Abstract):\n')
    file_src = ''.join(cls_src.file_lines)

    column = 13

    env_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..'))
    real_env_exe = os.path.join(env_path, 'bin', 'python')

    if pydevd.is_running():
        env_exe_proxy_src = '\n'.join([
            '#!/bin/sh',
            f'exec {shlex.quote(os.path.abspath(real_env_exe))} "$@"',
            '',
        ])

        tmp_dir = tempfile.mkdtemp()
        env_exe_proxy = os.path.join(tmp_dir, 'jedi-interpreter')

        with open(env_exe_proxy, 'w') as f:
            f.write(env_exe_proxy_src)

        os.chmod(env_exe_proxy, 0o755)

        env_exe = env_exe_proxy

    else:
        env_exe = real_env_exe

    try:
        # script = jedi.Interpreter(
        #     file_src,
        #     path=cls_src.file,
        #     namespaces=[locals(), globals()],
        # )

        env = jedi.api.environment.Environment(
            env_exe,
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
