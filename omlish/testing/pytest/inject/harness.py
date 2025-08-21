import contextlib
import enum
import typing as ta

import pytest

from .... import check
from .... import inject as inj
from .... import lang
from .. import plugins


T = ta.TypeVar('T')


##


class PytestScope(enum.Enum):
    SESSION = enum.auto()
    PACKAGE = enum.auto()
    MODULE = enum.auto()
    CLASS = enum.auto()
    FUNCTION = enum.auto()


class Scopes(lang.Namespace, lang.Final):
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


##


_ACTIVE_HARNESSES: set['Harness'] = set()


class Harness:
    def __init__(self, es: inj.Elements) -> None:
        super().__init__()

        self._orig_es = es
        self._es = inj.as_elements(
            inj.bind(self),
            *[
                inj.as_elements(
                    inj.bind_scope(ss),
                    inj.bind_scope_seed(inj.Key(pytest.FixtureRequest, tag=pts), ss),
                )
                for pts, ss in _SCOPES_BY_PYTEST_SCOPE.items()
            ],
            es,
        )
        self._inj: inj.Injector | None = None

    ##

    @contextlib.contextmanager
    def _activate(self) -> ta.Generator[ta.Self]:
        check.none(self._inj)
        check.not_in(self, _ACTIVE_HARNESSES)
        _ACTIVE_HARNESSES.add(self)
        try:
            with inj.create_managed_injector(self._es) as i:
                self._inj = i
                yield self
        finally:
            self._inj = None
            _ACTIVE_HARNESSES.remove(self)

    ##

    def __getitem__(
            self,
            target: inj.Key[T] | type[T],
    ) -> T:
        return check.not_none(self._inj)[target]

    def session(self) -> pytest.FixtureRequest:
        return self[inj.Key(pytest.FixtureRequest, tag=PytestScope.SESSION)]

    def package(self) -> pytest.FixtureRequest:
        return self[inj.Key(pytest.FixtureRequest, tag=PytestScope.PACKAGE)]

    def module(self) -> pytest.FixtureRequest:
        return self[inj.Key(pytest.FixtureRequest, tag=PytestScope.MODULE)]

    def class_(self) -> pytest.FixtureRequest:
        return self[inj.Key(pytest.FixtureRequest, tag=PytestScope.CLASS)]

    def function(self) -> pytest.FixtureRequest:
        return self[inj.Key(pytest.FixtureRequest, tag=PytestScope.FUNCTION)]

    ##

    @contextlib.contextmanager
    def _pytest_scope_manager(
            self,
            pytest_scope: PytestScope,
            request: pytest.FixtureRequest,
    ) -> ta.Generator[None]:
        ss = _SCOPES_BY_PYTEST_SCOPE[pytest_scope]
        with inj.enter_seeded_scope(check.not_none(self._inj), ss, {
            inj.Key(pytest.FixtureRequest, tag=pytest_scope): request,
        }):
            yield


##


@plugins.register
class HarnessPlugin:
    def __init__(self) -> None:
        super().__init__()

        self._harnesses_by_session: dict[ta.Any, Harness] = {}

    def get_session_harness(self, session: ta.Any) -> Harness:
        return self._harnesses_by_session[session]

    @pytest.fixture(scope='session', autouse=True)
    def _harness_scope_listener_session(self, request):
        with Harness(inj.as_elements(*_HARNESS_ELEMENTS_LIST))._activate() as harness:  # noqa
            self._harnesses_by_session[request.session] = harness
            try:
                with harness._pytest_scope_manager(PytestScope.SESSION, request):  # noqa
                    yield
            finally:
                del self._harnesses_by_session[request.session]

    @pytest.fixture(scope='package', autouse=True)
    def _harness_scope_listener_package(self, request):
        harness = self.get_session_harness(request.session)
        with harness._pytest_scope_manager(PytestScope.PACKAGE, request):  # noqa
            yield

    @pytest.fixture(scope='module', autouse=True)
    def _harness_scope_listener_module(self, request):
        harness = self.get_session_harness(request.session)
        with harness._pytest_scope_manager(PytestScope.MODULE, request):  # noqa
            yield

    @pytest.fixture(scope='class', autouse=True)
    def _harness_scope_listener_class(self, request):
        harness = self.get_session_harness(request.session)
        with harness._pytest_scope_manager(PytestScope.CLASS, request):  # noqa
            yield

    @pytest.fixture(scope='function', autouse=True)  # noqa
    def _harness_scope_listener_function(self, request):
        harness = self.get_session_harness(request.session)
        with harness._pytest_scope_manager(PytestScope.FUNCTION, request):  # noqa
            yield


##


_HARNESS_ELEMENTS_LIST: list[inj.Elements] = []


def register(*args: inj.Element | inj.Elements) -> None:
    _HARNESS_ELEMENTS_LIST.append(inj.as_elements(*args))


def bind(
        scope: PytestScope | str = PytestScope.SESSION,
        *,
        eager: bool = False,  # FIXME
) -> ta.Callable[[T], T]:
    def inner(obj):
        pts = scope if isinstance(scope, PytestScope) else PytestScope[check.isinstance(scope, str).upper()]
        register(inj.as_elements(
            inj.bind(obj, in_=_SCOPES_BY_PYTEST_SCOPE[pts]),
        ))
        return obj
    return inner


@pytest.fixture
def harness(request) -> Harness:
    pm = request.session.config.pluginmanager
    hp = check.single(p for n, p in pm.list_name_plugin() if isinstance(p, HarnessPlugin))
    return hp.get_session_harness(request.session)
