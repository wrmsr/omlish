import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang
from omlish import reflect as rfl

from .... import minichain as mc
from . import _inject


ItemT = ta.TypeVar('ItemT')


##


@ta.final
class ItemsBinderHelper(ta.Generic[ItemT]):
    def __init__(self, items_cls: ta.Any) -> None:
        self._items_cls = items_cls

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
            f'{ItemsBinderHelper._ItemsBox.__qualname__}${sfx}@{id(self):x}',
            (ItemsBinderHelper._ItemsBox,),
            {},
        )

    @cached.property
    def _set_key(self) -> inj.Key:
        return inj.as_key(ta.AbstractSet[self._item_rty])  # type: ignore

    def bind_items(self, *items: ItemT) -> inj.Elemental:
        return inj.bind_set_entry_const(self._set_key, self._items_box(items))

    def bind_items_provider(self) -> inj.Elements:
        return inj.as_elements(
            inj.set_binder[self._item_rty](),  # type: ignore
            inj.bind(
                lang.typed_lambda(self._items_cls, s=self._set_key)(
                    lambda s: self._items_cls([v for i in s for v in i.vs]),
                ),
                singleton=True,
            ),
        )


##


CHAT_OPTIONS_BINDER_HELPER = ItemsBinderHelper[mc.ChatChoicesOption](_inject.ChatChoicesServiceOptions)
bind_chat_options = CHAT_OPTIONS_BINDER_HELPER.bind_items

BACKEND_CONFIGS_BINDER_HELPER = ItemsBinderHelper[mc.Config](_inject.BackendConfigs)
bind_backend_configs = BACKEND_CONFIGS_BINDER_HELPER.bind_items


##


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
