# import contextlib
# import typing as ta

# from omlish import dataclasses as dc
# from omlish import lang

# from ...chat.messages import UserMessage
# from ...chat.models import ChatNew
# from ...chat.models import ChatOptions
# from ...chat.models import ChatOutput
# from ...chat.models import ChatRequest
# from ...generative import Generative
# from ...generative import MaxTokens
# from ...generative import Temperature
# from ...models import FinishReason
# from ...models import TokenUsage
# from ...streams import StreamService
# from ...streams import StreamServiceResponse
# from ..llamacpp import LlamacppChatModel


# if ta.TYPE_CHECKING:
#     import llama_cpp
#
#     from .... import llamacpp as lcu

# else:
#     llama_cpp = lang.proxy_import('llama_cpp')
#
#     lcu = lang.proxy_import('....llamacpp', __package__)


# T = ta.TypeVar('T')


##


# @dc.dataclass(frozen=True, kw_only=True)
# class Chat2Output:
#     token_usage: TokenUsage | None = dc.xfield(None, repr_fn=dc.opt_repr)
#     finish_reason: FinishReason | None = dc.xfield(None, repr_fn=dc.opt_repr)


# @dc.dataclass(frozen=True, kw_only=True)
# class Chat2Response(StreamServiceResponse[ChatOutput], lang.Final):
#     pass


# # @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
# class Chat2Model(  # noqa
#     StreamService[
#         ChatRequest,
#         ChatOptions,
#         ChatNew,
#         Chat2Response,
#     ],
#     Generative,
#     lang.Abstract,
# ):
#     pass


# class LlamacppChatStreamModel(Chat2Model):
#     def invoke(self, request: ChatRequest) -> Chat2Response:
#         raise NotImplementedError


##


# def _main() -> None:
#     request = ChatRequest.new(
#         [UserMessage('Is water dry?')],
#         Temperature(.1),
#         MaxTokens(64),
#     )
#
#     lcu.install_logging_hook()
#
#     with contextlib.ExitStack() as es:
#         llm = es.enter_context(contextlib.closing(llama_cpp.Llama(
#             model_path=LlamacppChatModel.model_path,
#             verbose=False,
#         )))
#
#         output = llm.create_chat_completion(
#             messages=[  # noqa
#                 dict(  # type: ignore
#                     role=LlamacppChatModel.ROLES_MAP[type(m)],
#                     content=LlamacppChatModel._get_msg_content(m),  # noqa
#                 )
#                 for m in request.v
#             ],
#             max_tokens=1024,
#             stream=True,
#             # stop=['\n'],
#         )
#
#         for chunk in output:
#             print(chunk)
#
#         # return ChatResponse(v=[
#         #     AiChoice(AiMessage(c['message']['content']))  # noqa
#         #     for c in output['choices']  # type: ignore
#         # ])


# if __name__ == '__main__':
#     _main()
