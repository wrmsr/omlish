# ruff: noqa: UP006 UP007 UP045
import abc
import dataclasses as dc
import http.client
import io
import os
import typing as ta
import urllib.request

from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from .targets import BytesDataServerTarget
from .targets import DataServerTarget
from .targets import FileDataServerTarget
from .targets import UrlDataServerTarget


DataServerTargetT = ta.TypeVar('DataServerTargetT', bound='DataServerTarget')


##


@dc.dataclass(frozen=True)
class DataServerRequest:
    method: str
    path: str


@dc.dataclass(frozen=True)
class DataServerResponse:
    status: int
    headers: ta.Optional[ta.Mapping[str, str]] = None
    body: ta.Optional[io.IOBase] = None

    #

    def close(self) -> None:
        if (body := self.body) is not None:
            body.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DataServerError(Exception):
    pass


class DataServerHandler(Abstract):
    @abc.abstractmethod
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        raise NotImplementedError


##


class DataServerTargetHandler(DataServerHandler, Abstract, ta.Generic[DataServerTargetT]):
    def __init__(self, target: DataServerTargetT) -> None:
        super().__init__()

        self._target = target

    #

    @classmethod
    def for_target(cls, tgt: DataServerTarget, **kwargs: ta.Any) -> 'DataServerTargetHandler':
        try:
            hc = _DATA_SERVER_TARGET_HANDLERS[type(tgt)]
        except KeyError:
            raise TypeError(tgt)  # noqa
        else:
            return hc(tgt, **kwargs)

    #

    def _make_headers(self) -> ta.Dict[str, str]:
        dct = {}
        if (ct := self._target.content_type) is not None:
            dct['Content-Type'] = ct
        if (cl := self._target.content_length) is not None:
            dct['Content-Length'] = str(cl)
        return dct


#


_DATA_SERVER_TARGET_HANDLERS: ta.Dict[ta.Type[DataServerTarget], ta.Type[DataServerTargetHandler]] = {}


def _register_data_server_target_handler(*tcs):
    def inner(hc):
        check.issubclass(hc, DataServerTargetHandler)
        for tc in tcs:
            check.issubclass(tc, DataServerTarget)
            check.not_in(tc, _DATA_SERVER_TARGET_HANDLERS)
            _DATA_SERVER_TARGET_HANDLERS[tc] = hc
        return hc
    return inner


#


@_register_data_server_target_handler(BytesDataServerTarget)
class BytesDataServerTargetHandler(DataServerTargetHandler[BytesDataServerTarget]):
    def _make_headers(self) -> ta.Dict[str, str]:
        dct = super()._make_headers()
        if 'Content-Length' not in dct and self._target.data is not None:
            dct['Content-Length'] = str(len(self._target.data))
        return dct

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in ('GET', 'HEAD'):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        return DataServerResponse(
            http.HTTPStatus.OK,
            headers=self._make_headers(),
            body=io.BytesIO(self._target.data) if self._target.data is not None and req.method == 'GET' else None,
        )


#


@_register_data_server_target_handler(FileDataServerTarget)
class FileDataServerTargetHandler(DataServerTargetHandler[FileDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method == 'HEAD':
            try:
                st = os.stat(check.not_none(self._target.file_path))
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            return DataServerResponse(
                http.HTTPStatus.OK,
                headers={
                    'Content-Length': str(st.st_size),
                    **self._make_headers(),
                },
            )

        elif req.method == 'GET':
            try:
                f = open(check.not_none(self._target.file_path), 'rb')  # noqa
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            try:
                sz = os.fstat(f.fileno())

                return DataServerResponse(
                    http.HTTPStatus.OK,
                    headers={
                        'Content-Length': str(sz.st_size),
                        **self._make_headers(),
                    },
                    body=f,  # noqa
                )

            except Exception:  # noqa
                f.close()
                raise

        else:
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)


#


@_register_data_server_target_handler(UrlDataServerTarget)
class UrlDataServerTargetHandler(DataServerTargetHandler[UrlDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in check.not_none(self._target.methods):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        resp: http.client.HTTPResponse = urllib.request.urlopen(urllib.request.Request(  # noqa
            method=req.method,
            url=check.not_none(self._target.url),
        ))

        try:
            return DataServerResponse(
                resp.status,
                headers=dict(resp.headers.items()),
                body=resp,
            )

        except Exception:  # noqa
            resp.close()
            raise
