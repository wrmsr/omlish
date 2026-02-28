from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import simple as _simple
    from . import types as _types


##


def bind_preparing() -> inj.Elements:
    els: list[inj.Elemental] = []

    els.append(inj.bind(_types.ChatPreparer, to_ctor=_simple.SimpleChatPreparer, singleton=True))

    return inj.as_elements(*els)
