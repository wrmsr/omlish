"""
Based on https://github.com/pgjones/hypercorn

TODO:
 - add ssl back lol
 - events as dc's
 - injectify
 - lifecycle / otp-ify
 - configify
"""
from .config import Config  # noqa
from .serving import serve  # noqa
