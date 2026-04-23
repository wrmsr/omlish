"""
TODO:
 - inspect .invoke method sigs
 - generic_mro
 - opt-in ability for classes to 'lie', explicitly provide their types
  - multi-dispatch? for RequestA output ResponseA, for RequestB output ResponseB, ...
 - eventually, COM-style QueryInterface w/ overloads?
"""
import typing as ta
import weakref

from omlish import check
from omlish import dataclasses as dc
from omlish import reflect as rfl

from ..resources import ResourceManaged
from .requests import Request
from .responses import Response
from .services import Service
from .stream import StreamResponseIterator


##


@dc.dataclass(frozen=True, kw_only=True)
class ReflectedService:
    request_v: rfl.Type
    request_option: rfl.Type

    response_v: rfl.Type
    response_output: rfl.Type


@dc.dataclass(frozen=True, kw_only=True)
class ReflectedStreamService(ReflectedService):
    stream_response_v: rfl.Type
    stream_response_output: rfl.Type


##


def reflect_service_like(req_rty: rfl.Type, resp_rty: rfl.Type) -> ReflectedService:
    req_rty = check.isinstance(req_rty, rfl.Generic)
    resp_rty = check.isinstance(resp_rty, rfl.Generic)

    check.is_(req_rty.cls, Request)
    check.is_(resp_rty.cls, Response)

    req_v_rty, req_opt_rty = req_rty.args
    resp_v_rty, resp_out_rty = resp_rty.args

    if isinstance(resp_v_rty, rfl.Generic) and resp_v_rty.cls is ResourceManaged:
        [resp_v_rmg] = resp_v_rty.args

        if isinstance(resp_v_rmg, rfl.Generic) and resp_v_rmg.cls is StreamResponseIterator:
            stream_resp_v_rty, stream_resp_out_rty = resp_v_rmg.args

            return ReflectedStreamService(
                request_v=req_v_rty,
                request_option=req_opt_rty,

                response_v=resp_v_rty,
                response_output=resp_out_rty,

                stream_response_v=stream_resp_v_rty,
                stream_response_output=stream_resp_out_rty,
            )

    return ReflectedService(
        request_v=req_v_rty,
        request_option=req_opt_rty,

        response_v=resp_v_rty,
        response_output=resp_out_rty,
    )


#


def reflect_service_cls_(service_cls: ta.Any) -> ReflectedService:
    rty = check.isinstance(rfl.type_(service_cls), rfl.Protocol)

    check.is_(rty.cls, Service)

    req_rty, resp_rty = rty.args

    return reflect_service_like(req_rty, resp_rty)


_REFLECT_SERVICE_CLS_CACHE: ta.MutableMapping[ta.Any, ReflectedService] = weakref.WeakKeyDictionary()


def reflect_service_cls(service_cls: ta.Any) -> ReflectedService:
    try:
        return _REFLECT_SERVICE_CLS_CACHE[service_cls]
    except KeyError:
        pass

    _REFLECT_SERVICE_CLS_CACHE[service_cls] = ret = reflect_service_cls_(service_cls)
    return ret


##


def is_stream_service_cls(service_cls: ta.Any) -> bool:
    return isinstance(reflect_service_cls(service_cls), ReflectedStreamService)
