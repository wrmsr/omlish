import typing as ta

from ... import check
from ... import dataclasses as dc
from ._compat import compat
from .cvs import Cvs
from .responses import Response
from .routes import Route
from .routes import RouteKey


if ta.TYPE_CHECKING:
    from .api import Api


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True, kw_only=True)
class AppRunParams:
    app: 'App'

    port: int | None = None


AppRunner: ta.TypeAlias = ta.Callable[[AppRunParams], None]


##


ViewFunc: ta.TypeAlias = ta.Callable[[], str]

BeforeRequestFunc: ta.TypeAlias = ta.Callable[[], Response | None]
AfterRequestFunc: ta.TypeAlias = ta.Callable[[ta.Any], ta.Any]


#


class App:
    _api: ta.ClassVar['Api']

    def __init__(
            self,
            import_name: str,
    ) -> None:
        check.not_none(self._api)

        super().__init__()

        self._import_name = check.non_empty_str(import_name)

        self._routes: set[Route] = set()
        self._routes_by_key: dict[RouteKey, Route] = {}

        self._view_funcs_by_endpoint: dict[str, ViewFunc] = {}

        self._before_request_funcs: list[BeforeRequestFunc] = []
        self._after_request_funcs: list[AfterRequestFunc] = []

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._import_name!r})'

    @property
    def import_name(self) -> str:
        return self._import_name

    ##
    # routing

    @property
    def routes(self) -> ta.AbstractSet[Route]:
        return self._routes

    @property
    def routes_by_key(self) -> ta.Mapping[RouteKey, Route]:
        return self._routes_by_key

    @property
    def view_funcs_by_endpoint(self) -> ta.Mapping[str, ViewFunc]:
        return self._view_funcs_by_endpoint

    @compat
    def get(self, rule: str, **options: ta.Any) -> ta.Callable[[T], T]:
        return self._method_route('GET', rule, **options)

    @compat
    def post(self, rule: str, **options: ta.Any) -> ta.Callable[[T], T]:
        return self._method_route('POST', rule, **options)

    @compat
    def put(self, rule: str, **options: ta.Any) -> ta.Callable[[T], T]:
        return self._method_route('PUT', rule, **options)

    @compat
    def delete(self, rule: str, **options: ta.Any) -> ta.Callable[[T], T]:
        return self._method_route('DELETE', rule, **options)

    @compat
    def patch(self, rule: str, **options: ta.Any) -> ta.Callable[[T], T]:
        return self._method_route('PATCH', rule, **options)

    def _method_route(
            self,
            method: str,
            rule: str,
            **options: ta.Any,
    ) -> ta.Callable[[T], T]:
        return self.route(
            rule,
            methods=[method],
            **options,
        )

    @compat
    def route(
            self,
            rule: str,
            **options: ta.Any,
    ) -> ta.Callable[[T], T]:
        def inner(fn):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, fn, **options)
            return fn

        return inner

    @compat
    def add_url_rule(
            self,
            rule: str,
            endpoint: str | None = None,
            view_func: ViewFunc | None = None,
            *,
            methods: ta.Iterable[str] | None = None,
    ) -> None:
        check.arg(check.non_empty_str(rule).startswith('/'))

        if endpoint is None:
            endpoint = check.not_none(view_func).__name__

        if methods is None:
            methods = ['GET']
        else:
            methods = [check.non_empty_str(m) for m in check.not_isinstance(methods, str)]
        methods = check.not_empty([s.upper() for s in methods])

        #

        route = Route(
            rule=rule,
            endpoint=endpoint,
            methods=frozenset(methods),
        )

        #

        for rk in route.keys:
            check.not_in(rk, self._routes_by_key)

        if view_func is not None:
            check.not_in(endpoint, self._view_funcs_by_endpoint)

        #

        self._routes.add(route)
        for rk in route.keys:
            self._routes_by_key[rk] = route

        if view_func is not None:
            self._view_funcs_by_endpoint[endpoint] = view_func

    ##
    # hooks

    @property
    def before_request_funcs(self) -> ta.Sequence[BeforeRequestFunc]:
        return self._before_request_funcs

    @property
    def after_request_funcs(self) -> ta.Sequence[AfterRequestFunc]:
        return self._after_request_funcs

    def before_request(self, func: T) -> T:  # BeforeRequestFunc
        self._before_request_funcs.append(ta.cast(BeforeRequestFunc, check.callable(func)))
        return func

    def after_request(self, func: T) -> T:  # AfterRequestFunc
        self._after_request_funcs.append(ta.cast(AfterRequestFunc, check.callable(func)))
        return func

    ##
    # running

    @compat
    def run(self, **kwargs: ta.Any) -> None:
        params = AppRunParams(app=self, **kwargs)
        runner = Cvs.APP_RUNNER.get()
        check.not_none(runner)(params)
