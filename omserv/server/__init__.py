"""
Based on https://github.com/pgjones/hypercorn

TODO:
 - !!! error handling jfc
 - add ssl back lol
 - events as dc's
 - injectify
 - lifecycle / otp-ify
 - configify

Lookit:
 - https://github.com/davidbrochart/anycorn
 - https://github.com/encode/starlette
 - https://github.com/tiangolo/fastapi
"""
from .config import Config  # noqa
from .workers import serve  # noqa
