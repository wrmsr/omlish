import typing as ta

from omlish import check
from omlish import lang

from ...prompts import PromptModel
from ...prompts import PromptRequest
from ...prompts import PromptResponse


if ta.TYPE_CHECKING:
    import openai
else:
    openai = lang.proxy_import('openai')


class OpenaiPromptModel(PromptModel):
    model = 'gpt-3.5-turbo-instruct'

    def __init__(self, *, api_key: str | None = None) -> None:
        super().__init__()
        self._api_key = api_key

    def invoke(self, t: PromptRequest) -> PromptResponse:
        client = openai.OpenAI(
            api_key=self._api_key,
        )

        response = client.completions.create(
            model=self.model,
            prompt=t.v,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.,
            presence_penalty=0.,
            stream=False,
        )

        choice = check.single(response.choices)
        return PromptResponse(v=choice.text)
