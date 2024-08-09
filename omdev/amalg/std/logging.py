"""
TODO:
 - debug
"""
import logging


log = logging.getLogger(__name__)


def setup_standard_logging() -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')
