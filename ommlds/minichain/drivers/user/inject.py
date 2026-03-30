from omlish import check
from omlish import inject as inj

from ...chat.messages import UserMessage
from ...chat.transform.metadata import CreatedAtAddingMessageTransform
from ...chat.transform.metadata import MessageUuidAddingMessageTransform
from ...chat.transform.metadata import OriginalMetadataStrippingMessageTransform
from ...chat.transform.types import CompositeMessageTransform
from ...chat.transform.types import MessageTransformChatTransform
from ..actions import SendUserMessagesAction
from ..inject import system_message_providers
from ..phases.injection import phase_callbacks
from ..phases.types import Phase
from ..phases.types import PhaseCallback
from ..types import DriverGetter
from .configs import UserConfig
from .preparing import InitialSystemMessageProvider
from .transforms import UserChatChatTransform


##


def bind_user(cfg: UserConfig = UserConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(UserChatChatTransform, to_const=MessageTransformChatTransform(
        CompositeMessageTransform([
            MessageUuidAddingMessageTransform(),
            CreatedAtAddingMessageTransform(),
            OriginalMetadataStrippingMessageTransform(),
        ]),
    )))

    #

    if cfg.initial_system_content is not None:
        els.extend([
            inj.bind(InitialSystemMessageProvider(cfg.initial_system_content)),
            system_message_providers().bind_item(to_key=InitialSystemMessageProvider),
        ])

    if cfg.initial_user_content is not None:
        async def add_initial_user_content(cdg: DriverGetter) -> None:
            await (await cdg()).do_action(
                SendUserMessagesAction([UserMessage(check.not_none(cfg.initial_user_content))]),
            )

        els.append(phase_callbacks().bind_item(to_fn=inj.KwargsTarget.of(
            lambda cdg: PhaseCallback(Phase.STARTED, lambda: add_initial_user_content(cdg)),
            cdg=DriverGetter,
        )))

    #

    return inj.as_elements(*els)
