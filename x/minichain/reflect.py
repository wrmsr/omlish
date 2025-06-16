"""
Approaches:
 - generic-replace inspect invoke signature param/return
"""
import inspect
import typing as ta

from omdev.home.secrets import install_env_secrets
from omlish import check
from omlish import dataclasses as dc
from omlish import reflect as rfl
from ommlds import minichain as mc


##


@dc.dataclass(frozen=True)
class ReflectedService:
    request_v: rfl.Type
    request_option: rfl.Type

    response_v: rfl.Type
    response_output: rfl.Type


def reflect_service(obj: ta.Any) -> ReflectedService:
    req_rty: rfl.Generic
    resp_rty: rfl.Generic

    if rfl.is_type(obj):
        rty = rfl.type_(obj)

        rty_proto = check.isinstance(rty, rfl.Protocol)
        check.is_(rty_proto.cls, mc.Service)

        req_rty, resp_rty = [check.isinstance(a, rfl.Generic) for a in rty_proto.args]

    else:
        invoke_sig = inspect.signature(obj.invoke)

        # FIXME: generic_mro
        req_rty = check.isinstance(rfl.type_(invoke_sig.parameters['request'].annotation), rfl.Generic)
        resp_rty = check.isinstance(rfl.type_(invoke_sig.return_annotation), rfl.Generic)

    check.is_(req_rty.cls, mc.Request)
    check.is_(resp_rty.cls, mc.Response)

    req_v_rty, req_opt_rty = req_rty.args
    resp_v_rty, resp_out_rty = resp_rty.args

    return ReflectedService(
        req_v_rty,
        req_opt_rty,

        resp_v_rty,
        resp_out_rty,
    )


##


ChatServiceFacade: ta.TypeAlias = mc.ServiceFacade[
    mc.Chat,
    mc.ChatOptions,
    mc.AiMessage,
    mc.ChatOutputs,
]


_chat_choices_stream_service_rfl = reflect_service(mc.ChatChoicesStreamService)
_chat_choices_service_rfl = reflect_service(mc.ChatChoicesService)
_chat_service_rfl = reflect_service(mc.ChatService)


@ta.overload
def as_chat_service(svc: mc.ChatChoicesStreamService) -> ChatServiceFacade: ...


@ta.overload
def as_chat_service(svc: mc.ChatChoicesService) -> ChatServiceFacade: ...


@ta.overload
def as_chat_service(svc: mc.ChatService) -> ChatServiceFacade: ...


def as_chat_service(svc):
    # g_mro = rfl.generic_mro(type(svc))

    svc_rfl = reflect_service(svc)

    if svc_rfl == _chat_choices_stream_service_rfl:
        return mc.ServiceFacade(
            mc.ChatChoicesServiceChatService(
                mc.ChatChoicesStreamServiceChatChoicesService(
                    svc,
                ),
            ),
        )

    if svc_rfl == _chat_choices_service_rfl:
        return mc.ServiceFacade(
            mc.ChatChoicesServiceChatService(
                svc,
            )
        )

    if svc_rfl == _chat_service_rfl:
        return mc.ServiceFacade(
            svc,
        )

    raise TypeError(svc)


##


def _main() -> None:
    install_env_secrets('openai_api_key')

    ccss = mc.registry_of[mc.ChatChoicesStreamService].new('openai')
    print(ccss)
    cs = as_chat_service(ccss)
    ta.reveal_type(cs)
    print(cs)
    # print(cs([mc.UserMessage('hi')]).v)

    ccs = mc.registry_of[mc.ChatChoicesService].new('openai')
    print(ccs)
    cs = as_chat_service(ccs)
    print(cs)
    # print(cs([mc.UserMessage('hi')]).v)


if __name__ == '__main__':
    _main()
