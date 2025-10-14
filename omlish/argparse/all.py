# ruff: noqa: I001
import argparse

from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    from .cli import (  # noqa
        ArgparseArg as Arg,
        argparse_arg as arg,
        argparse_arg_ as arg_,

        ArgparseCmdFn as CmdFn,
        ArgparseCmd as Cmd,
        argparse_cmd as cmd,

        ArgparseCli as Cli,
    )

    from .utils import (  # noqa
        NoExitArgumentParser,
    )


##


SUPPRESS = argparse.SUPPRESS

OPTIONAL = argparse.OPTIONAL
ZERO_OR_MORE = argparse.ZERO_OR_MORE
ONE_OR_MORE = argparse.ONE_OR_MORE
PARSER = argparse.PARSER
REMAINDER = argparse.REMAINDER

HelpFormatter = argparse.HelpFormatter
RawDescriptionHelpFormatter = argparse.RawDescriptionHelpFormatter
RawTextHelpFormatter = argparse.RawTextHelpFormatter
ArgumentDefaultsHelpFormatter = argparse.ArgumentDefaultsHelpFormatter

MetavarTypeHelpFormatter = argparse.MetavarTypeHelpFormatter

ArgumentError = argparse.ArgumentError
ArgumentTypeError = argparse.ArgumentTypeError

Action = argparse.Action
BooleanOptionalAction = argparse.BooleanOptionalAction
SubParsersAction = argparse._SubParsersAction  # noqa

FileType = argparse.FileType

Namespace = argparse.Namespace

ArgumentParser = argparse.ArgumentParser
