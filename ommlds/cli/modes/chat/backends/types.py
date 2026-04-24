import typing as ta

from omlish import lang

from ..... import minichain as mc


##


InitialBackendSpec = ta.NewType('InitialBackendSpec', mc.BackendSpec)


class BackendSpecGetter(lang.AsyncCachedFunc0[mc.BackendSpec]):
    pass
