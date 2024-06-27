import contextlib
import enum
import typing as ta

from _pytest.fixtures import FixtureRequest  # noqa
import pytest

from .... import inject as inj
from ....dev import pytest as ptu


class PytestScope(enum.Enum):
    SESSION = enum.auto()
    PACKAGE = enum.auto()
    MODULE = enum.auto()
    CLASS = enum.auto()
    FUNCTION = enum.auto()


_HARNESS_ELEMENTS_LIST: list[inj.Elements] = []
_ACTIVE_HARNESSES: set['Harness'] = set()

T = ta.TypeVar('T')


class Harness:
    def __init__(self, es: inj.Elements) -> None:
        super().__init__()
        self._inj = inj.create_injector(inj.as_elements(
            inj.as_binding(self),
            es,
        ))

    def __enter__(self: ta.Self) -> ta.Self:
        _ACTIVE_HARNESSES.add(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _ACTIVE_HARNESSES.remove(self)

    def __getitem__(
            self,
            target: ta.Union[inj.Key[T], type[T]],
    ) -> T:
        return self._inj[target]

    @contextlib.contextmanager
    def pytest_scope_manager(
            self,
            pytest_scope: PytestScope,
            request: FixtureRequest,
    ) -> ta.Generator[None, None, None]:
        yield


@ptu.plugins.register
class HarnessPlugin:

    @pytest.fixture(scope='session', autouse=True)
    def _harness_scope_listener_session(self, harness, request):
        with harness.pytest_scope_manager(PytestScope.SESSION, request):
            yield

    @pytest.fixture(scope='package', autouse=True)
    def _harness_scope_listener_package(self, harness, request):
        with harness.pytest_scope_manager(PytestScope.PACKAGE, request):
            yield

    @pytest.fixture(scope='module', autouse=True)
    def _harness_scope_listener_module(self, harness, request):
        with harness.pytest_scope_manager(PytestScope.MODULE, request):
            yield

    @pytest.fixture(scope='class', autouse=True)
    def _harness_scope_listener_class(self, harness, request):
        with harness.pytest_scope_manager(PytestScope.CLASS, request):
            yield

    @pytest.fixture(scope='function', autouse=True)
    def _harness_scope_listener_function(self, harness, request):
        with harness.pytest_scope_manager(PytestScope.FUNCTION, request):
            yield


@pytest.fixture(scope='session', autouse=True)
def harness() -> ta.Generator[Harness, None, None]:
    with Harness(inj.as_elements(*_HARNESS_ELEMENTS_LIST)) as harness:
        yield harness
