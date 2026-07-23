from omcore import check
from omcore import lang
from omcore.http import all as http
from omcore.secrets import all as sec

from ...types.backends import Backend
from ...types.models import Model


##


class BaseHttpBackend(Backend, lang.Abstract):
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

    @property
    def model(self) -> Model:
        return self._model
