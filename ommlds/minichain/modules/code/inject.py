from omlish import inject as inj
from omlish import lang

from ...drivers.preparing.injection import placeholder_contents_providers
from ...drivers.preparing.injection import system_message_providers
from .configs import CodeConfig


with lang.auto_proxy_import(globals()):
    from . import preparing as _preparing


##


def bind_code(cfg: CodeConfig = CodeConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_preparing.CodeSystemMessageProvider, singleton=True),
        system_message_providers().bind_item(to_key=_preparing.CodeSystemMessageProvider),
    ])

    els.extend([
        inj.bind(_preparing.CodePlaceholderContentsProvider, singleton=True),
        placeholder_contents_providers().bind_item(to_key=_preparing.CodePlaceholderContentsProvider),  # noqa
    ])

    #

    return inj.as_elements(*els)
