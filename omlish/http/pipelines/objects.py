# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from ...io.streams.types import BytesLike
from ...lite.abstract import Abstract
from ...lite.check import check
from ..headers import HttpHeaders
from ..parsing import ParsedHttpMessage
from ..versions import HttpVersion


##


class IoPipelineHttpMessageObject(Abstract):
    pass


#


class IoPipelineHttpMessageHead(IoPipelineHttpMessageObject, Abstract):
    @property
    @abc.abstractmethod
    def headers(self) -> HttpHeaders:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parsed(self) -> ta.Optional[ParsedHttpMessage]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> HttpVersion:
        raise NotImplementedError


#


class FullIoPipelineHttpMessage(IoPipelineHttpMessageObject, Abstract):
    @property
    @abc.abstractmethod
    def head(self) -> IoPipelineHttpMessageHead:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def body(self) -> BytesLike:
        raise NotImplementedError


#


@dc.dataclass(frozen=True)
class IoPipelineHttpMessageBodyData(IoPipelineHttpMessageObject, Abstract):
    data: BytesLike

    def __post_init__(self) -> None:
        check.arg(len(self.data) > 0)


#


@dc.dataclass(frozen=True)
class IoPipelineHttpMessageEnd(IoPipelineHttpMessageObject, Abstract):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpMessageAborted(IoPipelineHttpMessageObject, Abstract):
    reason: ta.Union[str, BaseException]

    @property
    def reason_str(self) -> str:
        if isinstance(r := self.reason, str):
            return r
        elif isinstance(r, BaseException):
            return repr(r)
        else:
            raise TypeError(r)


##


def _un_abstract_pipeline_http_object_classes() -> None:
    # So this is regrettable, but I think the benefits of having the base objects be actual dataclasses outweighs the
    # gnarliness here.
    for cls in [IoPipelineHttpMessageHead, FullIoPipelineHttpMessage]:
        atts = {a for a in cls.__dict__ if not a.startswith('_')}
        for att in atts:
            delattr(cls, att)
        ams = check.isinstance(getattr(cls, '__abstractmethods__'), frozenset)
        setattr(cls, '__abstractmethods__', ams - atts)


_un_abstract_pipeline_http_object_classes()


##


class IoPipelineHttpMessageObjects(Abstract):
    @property
    @abc.abstractmethod
    def _head_type(self) -> ta.Type[IoPipelineHttpMessageHead]:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_head(self, parsed: ParsedHttpMessage) -> IoPipelineHttpMessageHead:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def _full_type(self) -> ta.Type[FullIoPipelineHttpMessage]:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_full(self, head: IoPipelineHttpMessageHead, body: BytesLike) -> FullIoPipelineHttpMessage:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def _body_data_type(self) -> ta.Type[IoPipelineHttpMessageBodyData]:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_body_data(self, data: BytesLike) -> IoPipelineHttpMessageBodyData:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def _end_type(self) -> ta.Type[IoPipelineHttpMessageEnd]:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_end(self) -> ta.Any:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def _aborted_type(self) -> ta.Type[IoPipelineHttpMessageAborted]:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_aborted(self, reason: ta.Union[str, BaseException]) -> IoPipelineHttpMessageAborted:
        raise NotImplementedError
