"""
TODO:
 - pytest injector scopes:
  - lifecycle callbacks
 - still use pytest for parameterization
 - 'harness' dep?
 - inj mods reg in conftests?
  - watch imports
"""
import abc
import contextlib
import typing as ta
import warnings
import weakref

from _pytest.fixtures import FixtureRequest  # noqa
import pytest

from ... import scopes  # noqa
from .... import check
from .... import collections as ocol
from .... import dataclasses as dc
from .... import inject as inj
from .... import lang
from .... import lifecycles as lc
from ....dev.pytest.plugins import register_plugin


T = ta.TypeVar('T')


class PytestScope(lang.AutoEnum):
    SESSION = ...
    PACKAGE = ...
    MODULE = ...
    CLASS = ...
    FUNCTION = ...


PYTEST_SCOPES: ta.Sequence[PytestScope] = list(PytestScope)


class _InjectorScope(inj.Scope, lang.Abstract, lang.Sealed):

    def __init__(self) -> None:
        super().__init__()

        self._request_key = inj.Key(FixtureRequest, self.pytest_scope())
        self._state: ta.Optional[_InjectorScope.State] = None

    class State(dc.Pure):
        request: FixtureRequest
        values: ta.MutableMapping[inj.Binding, ta.Any] = dc.field(default_factory=ocol.IdentityKeyDict)

    @abc.abstractclassmethod
    def pytest_scope(cls) -> PytestScope:
        raise NotImplementedError

    def enter(self, request: FixtureRequest) -> None:
        check.none(self._state)
        check.state(request.scope == self.pytest_scope().name.lower())
        self._state = self.State(request)

    def exit(self) -> None:
        check.not_none(self._state)
        self._state = None

    def provide(self, binding: inj.Binding[T]) -> T:
        check.not_none(self._state)
        if binding.key == self._request_key:
            return self._state.request
        try:
            return self._state.values[binding]
        except KeyError:
            value = self._state.values[binding] = binding.provider()
            return value

    _subclass_map: ta.Mapping[PytestScope, ta.Type['_InjectorScope']] = {}

    @classmethod
    def _subclass(cls, ps: PytestScope):
        check.isinstance(ps, PytestScope)
        check.not_in(ps, cls._subclass_map)
        scls = type(
            ps.name.lower().capitalize() + cls.__name__,
            (cls, lang.Final),
            {
                'pytest_scope': classmethod(lambda _: ps),
                '__module__': cls.__module__,
            },
        )
        cls._subclass_map[ps] = scls
        return scls


Session = _InjectorScope._subclass(PytestScope.SESSION)
Package = _InjectorScope._subclass(PytestScope.PACKAGE)
Module = _InjectorScope._subclass(PytestScope.MODULE)
Class = _InjectorScope._subclass(PytestScope.CLASS)
Function = _InjectorScope._subclass(PytestScope.FUNCTION)


class _ScopeProvisionListener:

    def __init__(self) -> None:
        super().__init__()

        self._stack = []

    class Entry(ta.NamedTuple):
        binding: inj.Binding
        pytest_scope: ta.Optional[PytestScope]

    def __call__(self, injector, key, fn):
        binding = check.isinstance(injector.get_binding(key), inj.Binding)
        if issubclass(binding.scoping, _InjectorScope):
            pytest_scope = binding.scoping.pytest_scope()
        else:
            pytest_scope = None

        if self._stack:
            cur = self._stack[-1]
            if pytest_scope is not None:
                check.not_none(cur.pytest_scope)
                check.state(pytest_scope.value <= cur.pytest_scope.value)
                pytest_scope = min(pytest_scope, cur.pytest_scope, key=lambda s: s.value)
            else:
                if issubclass(binding.scoping, _CurrentInjectorScope):
                    pytest_scope = check.not_none(cur.pytest_scope)

        elif pytest_scope is not None:
            # TODO: check early that pytest_scope is active
            pass

        else:
            for inj_scope in injector._scopes.values():
                if isinstance(inj_scope, _InjectorScope) and inj_scope._state is not None:
                    inj_pytest_scope = inj_scope.pytest_scope()
                    if pytest_scope is None:
                        pytest_scope = inj_pytest_scope
                    else:
                        pytest_scope = max(pytest_scope, inj_pytest_scope, key=lambda s: s.value)

        ent = self.Entry(binding, pytest_scope)
        self._stack.append(ent)
        try:
            return fn()
        finally:
            popped = self._stack.pop()
            check.state(popped is ent)


class _CurrentInjectorScope(inj.Scope, lang.Final):

    def provide(self, binding: inj.Binding[T]) -> T:
        check.state(binding.key.annotation is None)
        injector = inj.Injector.current
        spl = injector[_ScopeProvisionListener]
        pytest_scope = check.not_none(spl._stack[-1].pytest_scope)
        new_key = inj.Key(binding.key.type, pytest_scope)
        return injector[new_key]


class _LifecycleRegistrar:

    def __init__(self) -> None:
        super().__init__()

        self._seen = weakref.WeakSet()
        self._stack: ta.List[_LifecycleRegistrar.State] = []

    class State(dc.Pure):
        key: inj.Key
        dependencies: ta.List[ta.Tuple[inj.Binding, ta.Any]] = dc.field(default_factory=list)

    def __call__(self, injector: inj.Injector, key, fn):
        st = self.State(key)
        self._stack.append(st)
        try:
            instance = fn()
        finally:
            popped = self._stack.pop()
            check.state(popped is st)

        if isinstance(instance, lc.Lifecycle) and not isinstance(instance, lc.LifecycleManager):
            binding = check.isinstance(injector.get_binding(key), inj.Binding)
            if self._stack:
                self._stack[-1].dependencies.append((binding, instance))

            if instance not in self._seen:
                inj_scope = check.issubclass(binding.scoping, _InjectorScope)
                man: lc.LifecycleManager = injector.get(inj.Key(lc.LifecycleManager, inj_scope.pytest_scope()))
                deps = [o for b, o in st.dependencies if b.scoping == binding.scoping]
                man.add(instance, deps)
                self._seen.add(instance)

        elif self._stack:
            self._stack[-1].dependencies.extend(st.dependencies)

        return instance


class _Eager(dc.Pure):
    key: inj.Key


class Harness:

    _ACTIVE = ocol.IdentitySet()

    def __init__(self, *binders: inj.Binder) -> None:
        super().__init__()

        binder = inj.create_binder()
        binder.bind(Harness, to_instance=self)

        for inj_scope in _InjectorScope._subclass_map.values():
            binder.bind_scope(inj_scope)
            binder.bind_callable(lambda: lang.raise_(RuntimeError), key=inj.Key(FixtureRequest, inj_scope.pytest_scope()), in_=inj_scope)  # noqa
            binder.bind(lc.LifecycleManager, annotated_with=inj_scope.pytest_scope(), in_=inj_scope)
            binder.new_set_binder(_Eager, annotated_with=inj_scope.pytest_scope(), in_=inj_scope)

        spl = _ScopeProvisionListener()
        binder.bind(_ScopeProvisionListener, to_instance=spl)
        binder.bind_provision_listener(spl)

        binder.bind_provision_listener(_LifecycleRegistrar())

        binder.bind_scope(_CurrentInjectorScope)

        binder.bind_callable(lambda: lang.raise_(RuntimeError), key=inj.Key(FixtureRequest), in_=_CurrentInjectorScope)
        binder.bind_callable(lambda: lang.raise_(RuntimeError), key=inj.Key(lc.LifecycleManager), in_=_CurrentInjectorScope)  # noqa

        self._injector = inj.create_injector(binder, *binders)

        self._inj_scopes_by_pytest_scope: ta.Mapping[PytestScope, _InjectorScope] = {
            s.pytest_scope(): self._injector._scopes[s]
            for s in _InjectorScope._subclass_map.values()
        }

    def __enter__(self):
        self._ACTIVE.add(self)
        return self

    def __exit__(self, et, e, tb):
        for s in self._inj_scopes_by_pytest_scope.values():
            if s._state is not None:
                warnings.warn(f'Scope {s.pytest_scope()} is still active')
        self._ACTIVE.remove(self)

    def __getitem__(
            self,
            target: ta.Union[inj.Key[T], ta.Type[T]],
    ) -> T:
        return self._injector[target]

    @contextlib.contextmanager
    def pytest_scope_manager(
            self,
            pytest_scope: PytestScope,
            request: FixtureRequest,
    ) -> ta.Generator[None, None, None]:
        check.isinstance(request, FixtureRequest)
        self._inj_scopes_by_pytest_scope[pytest_scope].enter(request)
        try:
            lm = self._injector[inj.Key(lc.LifecycleManager, pytest_scope)]
            with lc.context_manage(lm):
                eags = self._injector[inj.Key(ta.AbstractSet[_Eager], pytest_scope)]
                for eag in eags:
                    self._injector[eag.key]  # noqa
                yield
        finally:
            self._inj_scopes_by_pytest_scope[pytest_scope].exit()


@register_plugin
class HarnessPlugin:

    @pytest.fixture(scope='session', autouse=True)
    def harness(self) -> ta.Generator[Harness, None, None]:
        with Harness(*_HARNESS_BINDERS) as harness:
            yield harness

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


_HARNESS_BINDERS = []


def register(obj: T) -> T:
    check.empty(Harness._ACTIVE)
    if isinstance(obj, inj.Binder):
        _HARNESS_BINDERS.append(obj)
    else:
        raise TypeError(obj)
    return obj


def bind(inj_scope: ta.Type[_InjectorScope], *, eager: bool = False):
    def inner(obj):
        check.isinstance(obj, type)
        binder = register(inj.create_binder())
        binder.bind(obj, in_=inj_scope)
        if eager:
            binder.new_set_binder(_Eager, annotated_with=inj_scope.pytest_scope(), in_=inj_scope).bind(to_instance=_Eager(inj.Key(obj)))  # noqa
        return obj
    check.issubclass(inj_scope, _InjectorScope)
    return inner


def bind_instance(inj_scope: ta.Type[_InjectorScope], obj: T, **kwargs) -> T:
    check.issubclass(inj_scope, _InjectorScope)
    binder = register(inj.create_binder())
    binder.bind(type(obj), to_instance=obj, **kwargs)
    return obj
