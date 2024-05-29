"""distutils.pypirc

Provides the PyPIRCCommand class, the base class for the command classes
that uses .pypirc in the distutils.command package.
"""

import email.message
import os
from configparser import RawConfigParser

DEFAULT_PYPIRC = """\
[distutils]
index-servers =
    pypi

[pypi]
username:%s
password:%s
"""


def _extract_encoding(content_type):
    """
    >>> _extract_encoding('text/plain')
    'ascii'
    >>> _extract_encoding('text/html; charset="utf8"')
    'utf8'
    """
    msg = email.message.EmailMessage()
    msg['content-type'] = content_type
    return msg['content-type'].params.get('charset', 'ascii')
