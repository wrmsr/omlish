from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from .configs import CodeConfig


with lang.auto_proxy_import(globals()):
    from . import preparing as _preparing


##


def bind_code(cfg: CodeConfig = CodeConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_preparing.CodeSystemMessageProvider, singleton=True),
        mc.drivers.injection.system_message_providers().bind_item(to_key=_preparing.CodeSystemMessageProvider),
    ])

    els.extend([
        inj.bind(_preparing.CodePlaceholderContentsProvider, singleton=True),
        mc.drivers.injection.placeholder_contents_providers().bind_item(to_key=_preparing.CodePlaceholderContentsProvider),  # noqa
    ])

    #

    return inj.as_elements(*els)
