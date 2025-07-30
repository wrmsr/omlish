# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import argparse
import typing as ta

from .configs import DoerTaskArg


##


DOER_TASK_ARG_TYPE_NAMES_BY_TYPE: ta.Mapping[type, ta.Optional[str]] = {
    str: None,
    int: 'int',
    float: 'float',
    bool: 'bool',
}

DOER_TASK_ARG_TYPES_BY_TYPE_NAME: ta.Mapping[ta.Optional[str], type] = {
    v: k
    for k, v in DOER_TASK_ARG_TYPE_NAMES_BY_TYPE.items()
}


def build_doer_task_arg_parser(args: ta.Iterable[DoerTaskArg]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    for a in args:
        parser.add_argument(
            *([a.name] if isinstance(a.name, str) else (a.name or [])),
            **(dict(type=DOER_TASK_ARG_TYPES_BY_TYPE_NAME[a.type]) if a.type is not None else {}),  # type: ignore
            **(dict(nargs=a.nargs) if a.nargs else {}),  # type: ignore
            **(dict(default=a.default) if a.default is not None else {}),
        )

    return parser
