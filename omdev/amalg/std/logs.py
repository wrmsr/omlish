"""
TODO:
 - debug
"""
import logging
import typing as ta


log = logging.getLogger(__name__)


def setup_standard_logging(level: ta.Union[int, str] = logging.INFO) -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(level)
