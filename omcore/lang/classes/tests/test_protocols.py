import typing as ta

import pytest

from ...typing import static_check_issubclass
from ..protocols import ProtocolForbiddenAsBaseClass
from ..protocols import ProtocolForbiddenAsBaseClassTypeError


def test_protocol_forbidden_as_base_class() -> None:
    class FooProtocol(ProtocolForbiddenAsBaseClass, ta.Protocol):
        def foo(self) -> None: ...

    class BarProtocol(ProtocolForbiddenAsBaseClass, ta.Protocol):
        def bar(self) -> None: ...

    class JustFoo:
        def foo(self) -> None:
            pass

    static_check_issubclass[FooProtocol](JustFoo)
    static_check_issubclass[BarProtocol](JustFoo)  # type: ignore

    with pytest.raises(ProtocolForbiddenAsBaseClassTypeError):
        class JustBar(BarProtocol):  # noqa
            def bar(self) -> None:
                pass

    class FooBarProtocol(FooProtocol, BarProtocol, ta.Protocol):  # noqa
        pass

    with pytest.raises(TypeError):
        class NotAProtocol(ProtocolForbiddenAsBaseClass):  # noqa
            pass
