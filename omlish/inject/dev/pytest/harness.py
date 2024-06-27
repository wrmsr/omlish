import contextlib
import enum
import typing as ta

import pytest

from .... import check
from .... import lang
from .... import inject as inj
from ....dev import pytest as ptu


class PytestScope(enum.Enum):
    SESSION = enum.auto()
    PACKAGE = enum.auto()
    MODULE = enum.auto()
    CLASS = enum.auto()
    FUNCTION = enum.auto()


class Scopes(lang.Namespace):
    Session = inj.SeededScope(PytestScope.SESSION)
    Package = inj.SeededScope(PytestScope.PACKAGE)
    Module = inj.SeededScope(PytestScope.MODULE)
    Class = inj.SeededScope(PytestScope.CLASS)
    Function = inj.SeededScope(PytestScope.FUNCTION)


_SCOPES_BY_PYTEST_SCOPE: ta.Mapping[PytestScope, inj.SeededScope] = {
    check.isinstance(a.tag, PytestScope): a
    for n, a in Scopes.__dict__.items()
    if isinstance(a, inj.SeededScope)
}


_HARNESS_ELEMENTS_LIST: list[inj.Elements] = []
_ACTIVE_HARNESSES: set['Harness'] = set()

T = ta.TypeVar('T')


class Harness:
    def __init__(self, es: inj.Elements) -> None:
        super().__init__()
        self._inj = inj.create_injector(inj.as_elements(
            inj.as_binding(self),
            *[
                inj.as_elements(
                    inj.bind_scope(ss),
                    inj.bind_scope_seed(ss, inj.Key(pytest.FixtureRequest, tag=pts)),
                )
                for pts, ss in _SCOPES_BY_PYTEST_SCOPE.items()
            ],
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
    def _pytest_scope_manager(
            self,
            pytest_scope: PytestScope,
            request: pytest.FixtureRequest,
    ) -> ta.Generator[None, None, None]:
        ss = _SCOPES_BY_PYTEST_SCOPE[pytest_scope]
        with inj.enter_seeded_scope(self._inj, ss, {
            inj.Key(pytest.FixtureRequest, tag=pytest_scope): request,
        }):
            yield


@ptu.plugins.register
class HarnessPlugin:

    @pytest.fixture(scope='session', autouse=True)
    def _harness_scope_listener_session(self, harness, request):
        with harness._pytest_scope_manager(PytestScope.SESSION, request):  # noqa
            yield

    @pytest.fixture(scope='package', autouse=True)
    def _harness_scope_listener_package(self, harness, request):
        with harness._pytest_scope_manager(PytestScope.PACKAGE, request):  # noqa
            yield

    @pytest.fixture(scope='module', autouse=True)
    def _harness_scope_listener_module(self, harness, request):
        with harness._pytest_scope_manager(PytestScope.MODULE, request):  # noqa
            yield

    @pytest.fixture(scope='class', autouse=True)
    def _harness_scope_listener_class(self, harness, request):
        with harness._pytest_scope_manager(PytestScope.CLASS, request):  # noqa
            yield

    @pytest.fixture(scope='function', autouse=True)
    def _harness_scope_listener_function(self, harness, request):
        with harness._pytest_scope_manager(PytestScope.FUNCTION, request):  # noqa
            yield


@pytest.fixture(scope='session', autouse=True)
def harness() -> ta.Generator[Harness, None, None]:
    with Harness(inj.as_elements(*_HARNESS_ELEMENTS_LIST)) as harness:
        yield harness
