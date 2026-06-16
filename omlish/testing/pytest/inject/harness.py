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


class PytestScope(enum.StrEnum):
    SESSION = 'session'
    PACKAGE = 'package'
    MODULE = 'module'
    CLASS = 'class'
    FUNCTION = 'function'


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


_ACTIVE_HARNESSES: set[Harness] = set()


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

        for scope in PytestScope:
            self._install_scope_listener(scope)

    #

    def get_session_harness(self, session: ta.Any) -> Harness:
        return self._harnesses_by_session[session]

    @contextlib.contextmanager
    def _activate_scope(self, scope: PytestScope, request: pytest.FixtureRequest) -> ta.Generator[None]:
        if scope is PytestScope.SESSION:
            with Harness(inj.as_elements(*_HARNESS_ELEMENTS_LIST))._activate() as harness:  # noqa
                self._harnesses_by_session[request.session] = harness
                try:
                    with harness._pytest_scope_manager(scope, request):  # noqa
                        yield
                finally:
                    del self._harnesses_by_session[request.session]

        else:
            harness = self.get_session_harness(request.session)
            with harness._pytest_scope_manager(scope, request):  # noqa
                yield

    #

    def _make_scope_listener(self, scope: PytestScope) -> ta.Any:
        def func(request):
            with self._activate_scope(scope, request):
                yield

        func.__name__ = f'_harness_scope_listener_{scope.value}'
        func.__qualname__ = func.__name__

        return func

    def _install_scope_listener(self, scope: PytestScope) -> ta.Any:
        # Awful workaround for this asinine garbage:
        #  - https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
        #  - https://github.com/pytest-dev/pytest/pull/14071
        #  > When a class-scoped fixture is defined as an instance method, any attributes set on self will not be
        #    visible to test methods. This happens because pytest creates a new instance of the test class for each test
        #    method, while the fixture runs only once per class on a different instance.
        # This of course doesn't apply to fixtures from bound methods on plugin classes, but they still complain about
        # it anyway.
        func = self._make_scope_listener(scope)
        setattr(
            self,
            func.__name__,
            pytest.fixture(
                name=func.__name__,
                scope=scope.value,  # noqa
                autouse=True,
            )(func),
        )

        return func


##


_HARNESS_ELEMENTS_LIST: list[inj.Elements] = []


def register(*args: inj.Element | inj.Elements) -> None:
    _HARNESS_ELEMENTS_LIST.append(inj.as_elements(*args))


def bind(
        scope: PytestScope | str = PytestScope.SESSION,
        *,
        eager: bool = False,
) -> ta.Callable[[T], T]:
    def inner(obj):
        pts = scope if isinstance(scope, PytestScope) else PytestScope[check.isinstance(scope, str).upper()]
        register(inj.as_elements(
            inj.bind(obj, in_=_SCOPES_BY_PYTEST_SCOPE[pts], eager=eager),
        ))
        return obj
    return inner


@pytest.fixture
def harness(request) -> Harness:
    pm = request.session.config.pluginmanager
    hp = check.single(p for n, p in pm.list_name_plugin() if isinstance(p, HarnessPlugin))
    return hp.get_session_harness(request.session)
