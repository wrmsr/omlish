import dataclasses as dc
import typing as ta


class AwsLogMessageSubmitter:
    DEFAULT_URL = 'https://logs.{region_name}.amazonaws.com/'

    DEFAULT_HEADERS: ta.Mapping[str, str] = {
        'X-Amz-Target': 'Logs_20140328.PutLogEvents',
        'Content-Type': 'application/x-amz-json-1.1',
    }

    DEFAULT_SERVICE_NAME = 'logs'

    def __init__(
            self,
            region_name: str,
            *,
            url: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._region_name = region_name

        if url is None:
            url = self.DEFAULT_URL.format(region_name=region_name)
        self._url = url
