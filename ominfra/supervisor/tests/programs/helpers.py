# ruff: noqa: UP006 UP007 UP045
"""Shared utilities for test fixture programs."""
import sys


##


def log(msg: str) -> None:
    """Log message to stdout with flush for immediate visibility."""
    print(msg, flush=True)


def err(msg: str) -> None:
    """Log message to stderr with flush for immediate visibility."""
    print(msg, file=sys.stderr, flush=True)
