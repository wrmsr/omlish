from omcore import check
from omcore.http import all as http
from omcore.secrets import all as sec

from ....types.backends import AiMessageStream
from ....types.backends import StreamBackend
from ....types.compat import OpenaiCompat
from ....types.context import Context
from ....types.models import Model
from ....types.options import Options


##


class OpenaiCompletionsStreamBackend(StreamBackend):
    def __init__(
            self,
            model: Model,
            *,
            api_key: sec.Secret | None = None,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._model = model
        self._api_key = api_key
        self._http_client = http_client

        self._model_http = check.not_none(model.http)
        self._base_url = check.non_empty_str(self._model_http.base_url).rstrip('/')

        if self._model.compat is not None:
            self._compat = check.isinstance(self._model.compat, OpenaiCompat)
        else:
            self._compat = OpenaiCompat()

    @property
    def model(self) -> Model:
        return self._model

    async def stream(self, context: Context, options: Options | None = None) -> AiMessageStream:
        raise NotImplementedError
