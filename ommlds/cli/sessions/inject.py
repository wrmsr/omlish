from omlish import inject as inj
from omlish import lang

from .chat.configs import ChatConfig
from .completion.configs import CompletionConfig
from .configs import SessionConfig
from .embedding.configs import EmbeddingConfig


with lang.auto_proxy_import(globals()):
    from .chat import inject as _chat
    from .completion import inject as _completion
    from .embedding import inject as _embedding


##


def bind_sessions(cfg: SessionConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

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

    return inj.as_elements(*els)
