import typing as ta

from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from .chat import configs as _chat_cfgs
    from .chat import inject as _chat_inj
    from .completion import configs as _completion_cfgs
    from .completion import inject as _completion_inj
    from .embedding import configs as _embedding_cfgs
    from .embedding import inject as _embedding_inj


##


def bind_sessions(cfg: ta.Any) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    if isinstance(cfg, _chat_cfgs.ChatConfig):
        els.append(_chat_inj.bind_chat(cfg))

    elif isinstance(cfg, _completion_cfgs.CompletionConfig):
        els.append(_completion_inj.bind_completion(cfg))

    elif isinstance(cfg, _embedding_cfgs.EmbeddingConfig):
        els.append(_embedding_inj.bind_embedding(cfg))

    else:
        raise TypeError(cfg)

    #

    return inj.as_elements(*els)
