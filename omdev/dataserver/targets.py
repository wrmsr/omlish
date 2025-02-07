# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.lite.dataclasses import dataclass_maybe_post_init
from omlish.lite.marshal import OBJ_MARSHALER_OMIT_IF_NONE


##


@dc.dataclass(frozen=True)
class DataServerTarget(abc.ABC):  # noqa
    content_type: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    content_length: ta.Optional[int] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    #

    @classmethod
    def of(
            cls,
            obj: ta.Union[
                'DataServerTarget',
                bytes,
                None,
            ] = None,
            *,

            file_path: ta.Optional[str] = None,
            url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> 'DataServerTarget':
        if isinstance(obj, DataServerTarget):
            check.none(file_path)
            check.none(url)
            check.empty(kwargs)
            return obj

        elif isinstance(obj, bytes):
            return BytesDataServerTarget(
                data=obj,
                **kwargs,
            )

        elif file_path is not None:
            check.none(obj)
            check.none(url)
            return FileDataServerTarget(
                file_path=file_path,
                **kwargs,
            )

        elif url is not None:
            check.none(obj)
            check.none(file_path)
            return UrlDataServerTarget(
                url=url,
                **kwargs,
            )

        else:
            raise TypeError('No target type provided')

    #

    @classmethod
    def of_bytes(cls, data: bytes) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data,
            content_type='application/octet-stream',
        )

    @classmethod
    def of_text(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='text/plain; charset=utf-8',
        )

    @classmethod
    def of_json(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='application/json; charset=utf-8',
        )

    @classmethod
    def of_html(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='text/html; charset=utf-8',
        )


@dc.dataclass(frozen=True)
class BytesDataServerTarget(DataServerTarget):
    data: ta.Optional[bytes] = None  # required


@dc.dataclass(frozen=True)
class FileDataServerTarget(DataServerTarget):
    file_path: ta.Optional[str] = None  # required

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.file_path)


@dc.dataclass(frozen=True)
class UrlDataServerTarget(DataServerTarget):
    url: ta.Optional[str] = None  # required
    methods: ta.Optional[ta.Sequence[str]] = None  # required

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.url)
        check.not_none(self.methods)
        check.not_isinstance(self.methods, str)
