import os.path
import typing as ta

from omlish import lang

from ..models import Request
from ..models import Response
from ..prompts import Prompt
from ..prompts import PromptModel_


if ta.TYPE_CHECKING:
    import llama_cpp
else:
    llama_cpp = lang.proxy_import('llama_cpp')


class LlamacppPromptModel(PromptModel_):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def generate(self, request: Request[Prompt]) -> Response[str]:
        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            request.v.s,
            max_tokens=1024,
            stop=['\n'],
        )

        return Response(output['choices'][0]['text'])


# class LlamacppChatLlm(ChatLlm):
#     model_path = os.path.join(
#         os.path.expanduser('~/.cache/huggingface/hub'),
#         'models--TheBloke--Llama-2-7B-Chat-GGUF',
#         'snapshots',
#         '191239b3e26b2882fb562ffccdd1cf0f65402adb',
#         'llama-2-7b-chat.Q5_0.gguf',
#     )
#
#     ROLES_MAP: ta.ClassVar[ta.Mapping[ChatRole, str]] = {
#         ChatRole.SYSTEM: 'system',
#         ChatRole.USER: 'user',
#         ChatRole.ASSISTANT: 'assistant',
#     }
#
#     def get_completion(self, messages: ta.Sequence[ChatMessage]) -> str:
#         llm = llama_cpp.Llama(
#             model_path=self.model_path,
#         )
#
#         output = llm.create_chat_completion(
#             messages=[  # noqa
#                 dict(
#                     role=self.ROLES_MAP[m.role],
#                     content=m.text,
#                 )
#                 for m in messages
#             ],
#             max_tokens=1024,
#             # stop=["\n"],
#         )
#
#         return output['choices'][0]['message']['content']
