# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - ominfra? no, circdep
"""
import base64
import dataclasses as dc
import datetime
import typing as ta
import urllib.parse
import xml.etree.ElementTree as ET

from omlish.asyncs.asyncio.utils import asyncio_wait_concurrent
from omlish.lite.check import check
from omlish.lite.timing import log_timing_context
from omlish.logs.modules import get_module_logger


log = get_module_logger(globals())  # noqa


##


class AzureBlockBlobUploader:
    """
    https://learn.microsoft.com/en-us/rest/api/storageservices/put-block
    https://learn.microsoft.com/en-us/rest/api/storageservices/put-block-list
    """

    DEFAULT_CONCURRENCY = 4

    @dc.dataclass(frozen=True)
    class Request:
        method: str
        url: str
        headers: ta.Optional[ta.Dict[str, str]] = None
        body: ta.Optional[bytes] = None

    @dc.dataclass(frozen=True)
    class Response:
        status: int
        headers: ta.Optional[ta.Mapping[str, str]] = None
        data: ta.Optional[bytes] = None

        def get_header(self, name: str) -> ta.Optional[str]:
            for k, v in (self.headers or {}).items():
                if k.lower() == name.lower():
                    return v
            return None

    def __init__(
            self,
            blob_url_with_sas: str,
            make_request: ta.Callable[[Request], ta.Awaitable[Response]],
            *,
            api_version: str = '2020-10-02',
            concurrency: int = DEFAULT_CONCURRENCY,
    ) -> None:
        """
        blob_url_with_sas should be of the form:
           https://<account>.blob.core.windows.net/<container>/<blob>?<SAS-token>
        """

        super().__init__()

        self._make_request = make_request
        self._api_version = api_version
        check.arg(concurrency >= 1)
        self._concurrency = concurrency

        parsed = urllib.parse.urlparse(blob_url_with_sas)
        self._base_url = f'{parsed.scheme}://{parsed.netloc}'
        parts = parsed.path.lstrip('/').split('/', 1)
        self._container = parts[0]
        self._blob_name = parts[1]
        self._sas = parsed.query

    def _headers(self) -> ta.Dict[str, str]:
        """Standard headers for Azure Blob REST calls."""

        now = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
        return {
            'x-ms-date': now,
            'x-ms-version': self._api_version,
        }

    @dc.dataclass(frozen=True)
    class FileChunk:
        in_file: str
        offset: int
        size: int

    async def _upload_file_chunk_(
            self,
            block_id: str,
            chunk: FileChunk,
    ) -> None:
        with open(chunk.in_file, 'rb') as f:  # noqa
            f.seek(chunk.offset)
            data = f.read(chunk.size)

        check.equal(len(data), chunk.size)

        params = {
            'comp': 'block',
            'blockid': block_id,
        }
        query = self._sas + '&' + urllib.parse.urlencode(params)
        url = f'{self._base_url}/{self._container}/{self._blob_name}?{query}'

        log.debug(f'Uploading azure blob chunk {chunk} with block id {block_id}')  # noqa

        resp = await self._make_request(self.Request(
            'PUT',
            url,
            headers=self._headers(),
            body=data,
        ))
        if resp.status not in (201, 202):
            raise RuntimeError(f'Put Block failed: {block_id=} {resp.status=}')

    async def _upload_file_chunk(
            self,
            block_id: str,
            chunk: FileChunk,
    ) -> None:
        with log_timing_context(f'Uploading azure blob chunk {chunk} with block id {block_id}'):
            await self._upload_file_chunk_(
                block_id,
                chunk,
            )

    async def upload_file(
            self,
            chunks: ta.List[FileChunk],
    ) -> ta.Dict[str, ta.Any]:
        block_ids = []

        # 1) Stage each block
        upload_tasks = []
        for idx, chunk in enumerate(chunks):
            # Generate a predictable block ID (must be URL-safe base64)
            raw_id = f'{idx:08d}'.encode()
            block_id = base64.b64encode(raw_id).decode('utf-8')
            block_ids.append(block_id)

            upload_tasks.append(self._upload_file_chunk(
                block_id,
                chunk,
            ))

        await asyncio_wait_concurrent(upload_tasks, self._concurrency)

        # 2) Commit block list
        root = ET.Element('BlockList')
        for bid in block_ids:
            elm = ET.SubElement(root, 'Latest')
            elm.text = bid
        body = ET.tostring(root, encoding='utf-8', method='xml')

        params = {'comp': 'blocklist'}
        query = self._sas + '&' + urllib.parse.urlencode(params)
        url = f'{self._base_url}/{self._container}/{self._blob_name}?{query}'

        log.debug(f'Putting azure blob chunk list block ids {block_ids}')  # noqa

        resp = await self._make_request(self.Request(
            'PUT',
            url,
            headers={
                **self._headers(),
                'Content-Type': 'application/xml',
            },
            body=body,
        ))
        if resp.status not in (200, 201):
            raise RuntimeError(f'Put Block List failed: {resp.status} {resp.data!r}')

        ret = {
            'status_code': resp.status,
            'etag': resp.get_header('ETag'),
        }

        log.debug(f'Uploaded azure blob chunk {ret}')  # noqa

        return ret
