# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.lite.dataclasses import dataclass_maybe_post_init


##


@dc.dataclass(frozen=True)
class DataServerTarget(abc.ABC):  # noqa
    content_type: ta.Optional[str] = None
    content_length: ta.Optional[int] = None

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


@dc.dataclass(frozen=True)
class BytesDataServerTarget(DataServerTarget):
    data: ta.Optional[bytes] = None


@dc.dataclass(frozen=True)
class FileDataServerTarget(DataServerTarget):
    file_path: ta.Optional[str] = None

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.file_path)


@dc.dataclass(frozen=True)
class UrlDataServerTarget(DataServerTarget):
    url: ta.Optional[str] = None
    methods: ta.Optional[ta.Container[str]] = None

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.url)
        check.not_none(self.methods)
        check.not_isinstance(self.methods, str)
