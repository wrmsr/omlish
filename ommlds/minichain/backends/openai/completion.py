import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http

from ...completion import CompletionRequest
from ...completion import CompletionResponse
from ...completion import CompletionService
from ...configs import Config
from ...configs import consume_configs
from ...standard import ApiKey


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(name='openai', type='CompletionService')
class OpenaiCompletionService(CompletionService):
    DEFAULT_MODEL_NAME: ta.ClassVar[str] = 'gpt-3.5-turbo-instruct'

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')

    def invoke(self, t: CompletionRequest) -> CompletionResponse:
        raw_request = dict(
            model=self.DEFAULT_MODEL_NAME,
            prompt=t.prompt,
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
        return CompletionResponse(choice['text'])
