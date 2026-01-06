import typing as ta

import pytest

from omlish import check
from omlish import lang

from ...services.requests import Request
from ...services.responses import Response
from ...services.services import Service
from ...types import Option
from ...types import Output
from ..instrument import InstrumentedService
from ..instrument import ListInstrumentedServiceEventSink
from ..services import wrap_service


FooRequest: ta.TypeAlias = Request[str, Option]
FooResponse: ta.TypeAlias = Response[str, Output]
FooService: ta.TypeAlias = Service[FooRequest, FooResponse]


class FooError(Exception):
    pass


class FooServiceImpl:
    async def invoke(self, request: FooRequest) -> FooResponse:
        if request.v == 'fail':
            raise FooError

        return FooResponse(f'foo({request.v})')


def test_instrument():
    svc: FooService = FooServiceImpl()

    assert lang.sync_await(svc.invoke(FooRequest('bar'))) == FooResponse(f'foo(bar)')

    with pytest.raises(FooError):
        lang.sync_await(svc.invoke(FooRequest('fail')))

    lst = ListInstrumentedServiceEventSink()
    svc = wrap_service(svc, InstrumentedService, lst)

    assert lang.sync_await(svc.invoke(FooRequest('bar'))) == FooResponse(f'foo(bar)')
    ev0, ev1 = lst.events
    assert check.not_none(ev0.req).v == 'bar'
    assert check.not_none(ev1.req).v == 'bar'
    assert check.not_none(ev1.resp).v == 'foo(bar)'

    with pytest.raises(FooError):
        lang.sync_await(svc.invoke(FooRequest('fail')))
    _, _, ev2, ev3 = lst.events
    assert check.not_none(ev2.req).v == 'fail'
    assert check.not_none(ev3.req).v == 'fail'
    assert isinstance(check.not_none(ev3).exc, FooError)
