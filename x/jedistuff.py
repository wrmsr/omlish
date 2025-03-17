"""
NOTE:
 - does not support match statement, but handles it gracefully enough for non-local indexing
  - https://github.com/davidhalter/parso/issues/138

TODO:
 - executing? asttokens?
"""
import os.path
import inspect

import jedi

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


def _main() -> None:
    cls = lang.Final
    cls_src = findsource(cls)
    check.state(cls_src.file_lines[cls_src.line] == 'class Final(Abstract):\n')
    file_src = ''.join(cls_src.file_lines)

    column = 13

    try:
        script = jedi.Interpreter(
            file_src,
            path=cls_src.file,
            namespaces=[locals(), globals()],
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
