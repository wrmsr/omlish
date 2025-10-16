import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang
from omlish import reflect as rfl

from .... import minichain as mc
from . import _inject


T = ta.TypeVar('T')


##


class SetConstBinderHelperItemsBinder(ta.Protocol[T]):
    def __call__(self, *items: T) -> inj.Elements: ...


@ta.final
class SetConstBinderHelper(ta.Generic[T]):
    @cached.property
    def _item_rty(self) -> rfl.Type:
        rty = check.isinstance(rfl.type_(rfl.get_orig_class(self)), rfl.Generic)
        check.is_(rty.cls, self.__class__)
        return check.single(rty.args)

    @dc.dataclass(frozen=True, eq=False)
    class _ItemsBox:
        vs: ta.Sequence

    @cached.property
    def _items_box(self) -> type[_ItemsBox]:
        if isinstance(item_rty := self._item_rty, type):
            sfx = item_rty.__qualname__
        else:
            sfx = str(item_rty).replace("'", '')

        return lang.new_type(  # noqa
            f'{SetConstBinderHelper._ItemsBox.__qualname__}${sfx}@{id(self):x}',
            (SetConstBinderHelper._ItemsBox,),
            {},
        )

    @cached.property
    def item_binder(self) -> SetConstBinderHelperItemsBinder[T]:
        print(self._items_box)
        raise NotImplementedError


CHAT_OPTIONS_BINDER_HELPER = SetConstBinderHelper[mc.ChatChoicesOption]()
BACKEND_CONFIGS_BINDER_HELPER = SetConstBinderHelper[mc.Config]()

bind_chat_options = CHAT_OPTIONS_BINDER_HELPER.item_binder


##


@dc.dataclass(frozen=True, eq=False)
class _InjectedChatOptions:
    vs: ta.Sequence['mc.ChatChoicesOption']


def bind_chat_options(*vs: 'mc.ChatChoicesOption') -> inj.Elements:
    return inj.bind_set_entry_const(ta.AbstractSet[_InjectedChatOptions], _InjectedChatOptions(vs))


def _bind_chat_options_provider() -> inj.Elements:
    return inj.as_elements(
        inj.set_binder[_InjectedChatOptions](),
        inj.bind(
            lang.typed_lambda(_inject.ChatChoicesServiceOptions, s=ta.AbstractSet[_InjectedChatOptions])(
                lambda s: _inject.ChatChoicesServiceOptions([v for i in s for v in i.vs]),
            ),
            singleton=True,
        ),
    )


##


@dc.dataclass(frozen=True, eq=False)
class _InjectedBackendConfigs:
    vs: ta.Sequence['mc.Config']


def bind_backend_config(*vs: 'mc.Config') -> inj.Elements:
    return inj.bind_set_entry_const(ta.AbstractSet[_InjectedBackendConfigs], _InjectedBackendConfigs(vs))


def _bind_backend_configs_provider() -> inj.Elements:
    return inj.as_elements(
        inj.set_binder[_InjectedBackendConfigs](),
        inj.bind(
            lang.typed_lambda(_inject.BackendConfigs, s=ta.AbstractSet[_InjectedBackendConfigs])(
                lambda s: _inject.BackendConfigs([v for i in s for v in i.vs]),
            ),
            singleton=True,
        ),
    )


# ##
#
#
# def bind_chat_session(cfg: ChatSession.Config) -> inj.Elements:
#     els: list[inj.Elemental] = []
#
#     #
#
#     els.extend([
#         inj.set_binder[_InjectedChatOptions](),
#         inj.bind(
#             lang.typed_lambda(ChatOptions, s=ta.AbstractSet[_InjectedChatOptions])(
#                 lambda s: ChatOptions([co for ico in s for co in ico.v]),
#             ),
#             singleton=True,
#         ),
#     ])
#
#     #
#
#     els.extend([
#         inj.bind(StateStorageChatStateManager, singleton=True),
#         inj.bind(ChatStateManager, to_key=StateStorageChatStateManager),
#     ])
#
#     #
#
#     if cfg.markdown:
#         els.extend([
#             inj.bind(MarkdownStringChatSessionPrinter, singleton=True),
#             inj.bind(ChatSessionPrinter, to_key=MarkdownStringChatSessionPrinter),
#         ])
#     else:
#         els.extend([
#             inj.bind(SimpleStringChatSessionPrinter, singleton=True),
#             inj.bind(ChatSessionPrinter, to_key=SimpleStringChatSessionPrinter),
#         ])
#
#     #
#
#     if cfg.dangerous_no_tool_confirmation:
#         els.extend([
#             inj.bind(NopToolExecutionConfirmation, singleton=True),
#             inj.bind(ToolExecutionConfirmation, to_key=NopToolExecutionConfirmation),
#         ])
#     else:
#         els.extend([
#             inj.bind(AskingToolExecutionConfirmation, singleton=True),
#             inj.bind(ToolExecutionConfirmation, to_key=AskingToolExecutionConfirmation),
#         ])
#
#     #
#
#     els.extend([
#         inj.bind(ToolUseExecutorImpl, singleton=True),
#         inj.bind(ToolUseExecutor, to_key=ToolUseExecutorImpl),
#     ])
#
#     #
#
#     return inj.as_elements(*els)
