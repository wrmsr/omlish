import typing as ta

from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import base as _base


##


Commands = ta.NewType('Commands', ta.Sequence['_base.Command'])
