from __future__ import absolute_import


long = int
basestring = str
raw_input = input
unichr = chr


class unicode(str):
    def __init__(self, string, encoding, errors):
        str.__init__(self, string)


def as_bytes(s, encoding='utf8'):
    if isinstance(s, bytes):
        return s
    else:
        return s.encode(encoding)


def as_string(s, encoding='utf8'):
    if isinstance(s, str):
        return s
    else:
        return s.decode(encoding)


def is_text_stream(stream):
    import _io
    return isinstance(stream, _io._TextIOBase)


import xmlrpc.client as xmlrpclib

import urllib.parse as urlparse
import urllib.parse as urllib

from hashlib import sha1

import syslog

import configparser as ConfigParser

from io import StringIO

from sys import maxsize as maxint

import http.client as httplib

from base64 import decodebytes as decodestring, encodebytes as encodestring

from xmlrpc.client import Fault

from string import ascii_letters as letters

from hashlib import md5

import _thread as thread

StringTypes = (str,)

from html import escape

import html.entities as htmlentitydefs

from html.parser import HTMLParser

# Begin importlib/setuptools compatibility code

# Supervisor used pkg_resources (a part of setuptools) to load package
# resources for 15 years, until setuptools 67.5.0 (2023-03-05) deprecated
# the use of pkg_resources.  On Python 3.8 or later, Supervisor now uses
# importlib (part of Python 3 stdlib).  Unfortunately, on Python < 3.8,
# Supervisor needs to use pkg_resources despite its deprecation.  The PyPI
# backport packages "importlib-resources" and "importlib-metadata" couldn't
# be added as dependencies to Supervisor because they require even more
# dependencies that would likely cause some Supervisor installs to fail.
from warnings import filterwarnings as _fw


_fw("ignore", message="pkg_resources is deprecated as an API")

from importlib.metadata import EntryPoint as _EntryPoint

def import_spec(spec):
    return _EntryPoint(None, spec, None).load()

import importlib.resources as _importlib_resources

def resource_filename(package, path):
    return str(_importlib_resources.files(package).joinpath(path))
