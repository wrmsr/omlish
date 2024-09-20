import typing as ta

from omlish import lang

from ..models import Request
from ..models import Response
from ..prompts import Prompt
from ..prompts import PromptModel


if ta.TYPE_CHECKING:
    import openai
else:
    openai = lang.proxy_import('openai')


class OpenaiPromptModel(PromptModel):
    model = 'gpt-3.5-turbo-instruct'

    def generate(self, t: Request[Prompt]) -> Response[str]:
        response = openai.completions.create(
            model=self.model,
            prompt=t.v.s,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.,
            presence_penalty=0.,
            stream=False,
        )

        return Response(response.choices[0].text)
