import os

from omlish import check
from omlish.formats import json
from omlish.http import all as http
from omlish.secrets.secrets import Secret

from ...prompts import PromptModel
from ...prompts import PromptRequest
from ...prompts import PromptResponse


class OpenaiPromptModel(PromptModel):
    model = 'gpt-3.5-turbo-instruct'

    def __init__(
            self,
            *,
            api_key: Secret | str | None = None,
    ) -> None:
        super().__init__()
        self._api_key = Secret.of(api_key if api_key is not None else os.environ['OPENAI_API_KEY'])

    def invoke(self, t: PromptRequest) -> PromptResponse:
        raw_request = dict(
            model=self.model,
            prompt=t.v,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.,
            presence_penalty=0.,
            stream=False,
        )

        raw_response = http.request(
            'https://api.openai.com/v1/completions',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        choice = check.single(response['choices'])
        return PromptResponse(v=choice['text'])
