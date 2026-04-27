from omlish import inject as inj
from omlish import lang
from omlish import lifecycles as lc

from .chat.configs import ChatConfig
from .completion.configs import CompletionConfig
from .configs import EntrypointConfig
from .embedding.configs import EmbeddingConfig
from .types import ProfileName


with lang.auto_proxy_import(globals()):
    from . import asyncs
    from .chat import inject as _chat
    from .completion import inject as _completion
    from .embedding import inject as _embedding


##


def bind_main(
        *,
        entrypoint_cfg: EntrypointConfig,
        profile_name: str | None = None,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        lc.bind_async_lifecycle_registrar(),
        lc.bind_async_managed_lifecycle_manager(eager=True),
    ])

    #

    if profile_name is not None:
        els.append(inj.bind(ProfileName, to_const=profile_name))

    #

    if isinstance(entrypoint_cfg, ChatConfig):
        els.append(_chat.bind_chat(entrypoint_cfg))

    elif isinstance(entrypoint_cfg, CompletionConfig):
        els.append(_completion.bind_completion(entrypoint_cfg))

    elif isinstance(entrypoint_cfg, EmbeddingConfig):
        els.append(_embedding.bind_embedding(entrypoint_cfg))

    else:
        raise TypeError(entrypoint_cfg)

    #

    els.extend([
        inj.bind(asyncs.AsyncThreadRunner, to_ctor=asyncs.AsyncioAsyncThreadRunner),
    ])

    #

    return inj.as_elements(*els)
