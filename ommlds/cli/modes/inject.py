from omlish import inject as inj
from omlish import lang

from ... import minichain as mc
from .chat.configs import ChatConfig
from .completion.configs import CompletionConfig
from .configs import ModeConfig
from .embedding.configs import EmbeddingConfig
from .types import ProfileName


with lang.auto_proxy_import(globals()):
    from .chat import inject as _chat
    from .completion import inject as _completion
    from .embedding import inject as _embedding


##


def bind_modes(
        cfg: ModeConfig,
        *,
        profile_name: str | None = None,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    if profile_name is not None:
        els.append(inj.bind(ProfileName, to_const=profile_name))

    #

    if isinstance(cfg, ChatConfig):
        els.append(_chat.bind_chat(cfg))

    elif isinstance(cfg, CompletionConfig):
        els.append(_completion.bind_completion(cfg))

    elif isinstance(cfg, EmbeddingConfig):
        els.append(_embedding.bind_embedding(cfg))

    else:
        raise TypeError(cfg)

    #

    for mod_cfg in cfg.modules or []:
        els.extend(mc.modules.inject.bind_module(mod_cfg))

    #

    return inj.as_elements(*els)
