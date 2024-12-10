# ruff: noqa: I001
import argparse

from .cli import (  # noqa
    Arg,
    arg,

    CommandFn,
    Command,
    command,

    Cli,
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
