# @omlish-lite

from .find import (  # noqa
    chop_magic_block,
    chop_magic_lines,
    compile_magic_style_pat,
    find_magic,
    find_magic_files,
    find_magic_py_modules,
)

from .magic import (  # noqa
    Magic,
)

from .prepare import (  # noqa
    MagicPrepareError,
    json_magic_preparer,
    py_compile_magic_preparer,
    py_eval_magic_preparer,
)

from .styles import (  # noqa
    C_MAGIC_STYLE,
    MAGIC_KEY_PREFIX,
    MagicStyle,
    PY_MAGIC_STYLE,
)
