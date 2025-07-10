import json
import typing as ta


##


class MagicPrepareError(Exception):
    pass


def py_compile_magic_preparer(src: str) -> ta.Any:
    try:
        prepared = compile(f'({src})', '<magic>', 'eval')
    except SyntaxError:
        raise MagicPrepareError  # noqa
    return prepared


def py_eval_magic_preparer(src: str) -> ta.Any:
    code = py_compile_magic_preparer(src)
    return eval(code)  # noqa


def json_magic_preparer(src: str) -> ta.Any:
    try:
        prepared = json.loads(src)
    except json.JSONDecodeError:
        raise MagicPrepareError  # noqa
    return prepared
