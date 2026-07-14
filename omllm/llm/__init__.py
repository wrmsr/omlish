# fmt: off
# ruff: noqa: I001
from omcore import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from omcore import lang as _lang  # noqa


with _lang.auto_proxy_init(
        globals(),
        # disable=True,
        # eager=True,
):
    ##

    from .backends.openai.completion.backend import (  # noqa
        CompletionOpenaiBackend,
    )

    ##

    from .types.backends import (  # noqa
        Backend,
    )

    from .types.content import (  # noqa
        Content,
        ContentBuilder,

        TextContent,
        TextContentBuilder,

        ThinkingContent,
        ThinkingContentBuilder,
    )

    from .types.context import (  # noqa
        Context,
    )

    from .types.messages import (  # noqa
        Message,
        MessageBuilder,

        UserMessage,
        UserMessageBuilder,

        AiMessage,
        AiMessageBuilder,
    )

    from .types.options import (  # noqa
        Options,
    )
