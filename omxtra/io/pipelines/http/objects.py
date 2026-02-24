# ruff: noqa: UP045
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.versions import HttpVersion
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.lite.abstract import Abstract
from omlish.lite.check import check


##


class PipelineHttpHead(Abstract):
    @property
    @abc.abstractmethod
    def version(self) -> HttpVersion:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def headers(self) -> HttpHeaders:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parsed(self) -> ta.Optional[ParsedHttpMessage]:
        raise NotImplementedError


class FullPipelineHttpObject(Abstract):
    @property
    @abc.abstractmethod
    def head(self) -> PipelineHttpHead:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def body(self) -> BytesLikeOrMemoryview:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class PipelineHttpContentChunkData(Abstract):
    data: BytesLikeOrMemoryview


@dc.dataclass(frozen=True)
class PipelineHttpEnd(Abstract):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpAborted(Abstract):
    reason: str


##


def _un_abstract_pipeline_http_object_classes() -> None:
    # So this is regrettable, but I think the benefits of having the base objects be actual dataclases outweighs the
    # gnarliness here.
    for cls in [PipelineHttpHead, FullPipelineHttpObject]:
        atts = {a for a in cls.__dict__ if not a.startswith('_')}
        for att in atts:
            delattr(cls, att)
        ams = check.isinstance(getattr(cls, '__abstractmethods__'), frozenset)
        setattr(cls, '__abstractmethods__', ams - atts)


_un_abstract_pipeline_http_object_classes()
