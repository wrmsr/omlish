"""
TODO:
 - debug
"""
# ruff: noqa: UP007
import logging
import typing as ta


log = logging.getLogger(__name__)


def configure_standard_logging(level: ta.Union[int, str] = logging.INFO) -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(level)
