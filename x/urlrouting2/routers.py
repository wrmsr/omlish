# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import dataclasses as dc
import enum
import re
import typing as ta
import urllib.parse

from .converters import URL_ROUTE_DEFAULT_CONVERTERS
from .converters import UrlRouteConverter


UrlRouteEndpoint = ta.Any  # ta.TypeAlias
UrlRouteValues = ta.Mapping[str, ta.Any]  # ta.TypeAlias


##


class UrlRouteSlashStyle(enum.Enum):
    STRICT = 'strict'
    REDIRECT = 'redirect'
    IGNORE = 'ignore'


class UrlRouteMatchError(Exception):
    pass


@dc.dataclass(frozen=True)
class UrlRouteNotFoundError(UrlRouteMatchError):
    path: str


@dc.dataclass(frozen=True)
class UrlRouteMethodNotAllowedError(UrlRouteMatchError):
    path: str
    method: str
    allowed_methods: ta.AbstractSet[str]


@dc.dataclass(frozen=True)
class UrlRouteRedirectRequiredError(UrlRouteMatchError):
    path: str
    redirect_path: str


@dc.dataclass(frozen=True)
class UrlRoute:
    pattern: str
    endpoint: UrlRouteEndpoint = None

    methods: ta.Optional[ta.AbstractSet[str]] = None
    name: ta.Optional[str] = None
    slash_style: ta.Optional[UrlRouteSlashStyle] = None

    defaults: ta.Optional[ta.Mapping[str, ta.Any]] = None
    data: ta.Optional[ta.Mapping[str, ta.Any]] = None


@dc.dataclass(frozen=True)
class UrlRouteMatch:
    route: UrlRoute
    values: UrlRouteValues

    @property
    def endpoint(self) -> UrlRouteEndpoint:
        return self.route.endpoint


@dc.dataclass(frozen=True)
class UrlRouterConfig:
    slash_style: UrlRouteSlashStyle = UrlRouteSlashStyle.REDIRECT
    merge_slashes: bool = False
    add_head: bool = True


##


@dc.dataclass(frozen=True)
class _UrlRouteVariable:
    name: str
    converter: UrlRouteConverter


@dc.dataclass(frozen=True)
class _UrlRouteSegmentPattern:
    regex: ta.Pattern[str]
    variables: ta.Sequence[_UrlRouteVariable]
    weight: int
    is_greedy: bool = False


_UrlRoutePart = ta.Union[str, _UrlRouteSegmentPattern]  # ta.TypeAlias
_UrlRouteBuildPart = ta.Union[str, _UrlRouteVariable]  # ta.TypeAlias


@dc.dataclass(frozen=True)
class _CompiledUrlRoute:
    route: UrlRoute
    parts: ta.Sequence[_UrlRoutePart]
    build_parts: ta.Sequence[_UrlRouteBuildPart]
    methods: ta.Optional[ta.AbstractSet[str]]
    order: int


@dc.dataclass()
class _UrlRouteNode:
    static: ta.MutableMapping[str, '_UrlRouteNode'] = dc.field(default_factory=dict)
    dynamic: list[ta.Tuple[_UrlRouteSegmentPattern, '_UrlRouteNode']] = dc.field(default_factory=list)
    greedy: list[ta.Tuple[_UrlRouteSegmentPattern, _CompiledUrlRoute]] = dc.field(default_factory=list)
    routes: list[_CompiledUrlRoute] = dc.field(default_factory=list)


##


_URL_ROUTE_VARIABLE_RE = re.compile(
    r"""
    \{
        (?P<name>[a-zA-Z_][a-zA-Z0-9_]*)
        (?:
            :
            (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)
            (?:
                \(
                    (?P<args>[^{}]*)
                \)
            )?
        )?
    \}
    """,
    re.VERBOSE,
)


def _parse_url_route_converter_args(s: str) -> ta.Sequence[str]:
    if not s:
        return ()
    return tuple(p.strip() for p in s.split(',') if p.strip())


def _normalize_url_route_method_set(
        methods: ta.Optional[ta.AbstractSet[str]],
        *,
        add_head: bool,
) -> ta.Optional[ta.AbstractSet[str]]:
    if methods is None:
        return None

    ret = {m.upper() for m in methods}
    if add_head and 'GET' in ret:
        ret.add('HEAD')
    return frozenset(ret)


def _split_url_route_path(path: str) -> list[str]:
    if not path.startswith('/'):
        raise ValueError(path)

    if path == '/':
        return []

    return path[1:].split('/')


def _quote_url_route_static_part(s: str) -> str:
    return urllib.parse.quote(s, safe="!$&'()*+,/:;=@")


##


class UrlRouter:
    def __init__(
            self,
            routes: ta.Iterable[UrlRoute] = (),
            *,
            config: UrlRouterConfig = UrlRouterConfig(),
            converters: ta.Optional[ta.Mapping[str, ta.Callable[..., UrlRouteConverter]]] = None,
    ) -> None:
        super().__init__()

        self._config = config
        self._converters = dict(URL_ROUTE_DEFAULT_CONVERTERS)
        if converters is not None:
            self._converters.update(converters)

        self._root = _UrlRouteNode()
        self._routes: list[_CompiledUrlRoute] = []
        self._routes_by_name_or_endpoint: dict[ta.Any, list[_CompiledUrlRoute]] = {}

        for route in routes:
            self.add(route)

    @property
    def config(self) -> UrlRouterConfig:
        return self._config

    def add(self, route: UrlRoute) -> None:
        compiled = self._compile_route(route, len(self._routes))
        self._routes.append(compiled)
        if route.name is not None:
            self._routes_by_name_or_endpoint.setdefault(route.name, []).append(compiled)
        if route.endpoint is not None:
            self._routes_by_name_or_endpoint.setdefault(route.endpoint, []).append(compiled)
        self._insert(compiled)

    def match(
            self,
            path: str,
            *,
            method: ta.Optional[str] = None,
    ) -> UrlRouteMatch:
        path = urllib.parse.urlsplit(path).path or '/'
        original_path = path

        if self._config.merge_slashes:
            path = re.sub('/{2,}', '/', path)

        try:
            return self._match(path, method=method)
        except UrlRouteNotFoundError:
            pass

        alt_path = self._alternate_slash_path(path)
        if alt_path is not None:
            try:
                match = self._match(alt_path, method=method)
            except UrlRouteNotFoundError:
                pass
            else:
                slash_style = match.route.slash_style or self._config.slash_style
                if slash_style is UrlRouteSlashStyle.REDIRECT:
                    raise UrlRouteRedirectRequiredError(original_path, alt_path)
                if slash_style is UrlRouteSlashStyle.IGNORE:
                    return match

        raise UrlRouteNotFoundError(original_path)

    def allowed_methods(self, path: str) -> ta.AbstractSet[str]:
        try:
            self.match(path, method='__OMLISH_URL_ROUTER_METHOD_SENTINEL__')
        except UrlRouteMethodNotAllowedError as e:
            return e.allowed_methods
        except UrlRouteMatchError:
            return frozenset()
        else:
            return frozenset()

    def build(
            self,
            name_or_endpoint: ta.Any,
            values: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> str:
        values = values or {}
        for compiled in self._routes_by_name_or_endpoint.get(name_or_endpoint, ()):
            built = self._try_build(compiled, values)
            if built is not None:
                return built
        raise KeyError(name_or_endpoint)

    def _compile_route(self, route: UrlRoute, order: int) -> _CompiledUrlRoute:
        if not route.pattern.startswith('/'):
            raise ValueError(route.pattern)

        parts: list[_UrlRoutePart] = []
        build_parts: list[_UrlRouteBuildPart] = []

        for segment in _split_url_route_path(route.pattern):
            pattern, segment_build_parts = self._compile_segment(segment)
            parts.append(pattern)
            build_parts.extend(segment_build_parts)
            build_parts.append('/')

        if build_parts:
            build_parts.pop()

        return _CompiledUrlRoute(
            route=route,
            parts=tuple(parts),
            build_parts=tuple(build_parts),
            methods=_normalize_url_route_method_set(route.methods, add_head=self._config.add_head),
            order=order,
        )

    def _compile_segment(
            self,
            segment: str,
    ) -> ta.Tuple[_UrlRoutePart, ta.Sequence[_UrlRouteBuildPart]]:
        pos = 0
        regex_parts = []
        variables = []
        build_parts: list[_UrlRouteBuildPart] = []
        weight = 0
        is_greedy = False

        for m in _URL_ROUTE_VARIABLE_RE.finditer(segment):
            if m.start() > pos:
                static = segment[pos:m.start()]
                regex_parts.append(re.escape(static))
                build_parts.append(static)
                weight -= len(static)

            name = m.group('name')
            converter_name = m.group('converter') or 'str'
            converter_factory = self._converters.get(converter_name)
            if converter_factory is None:
                raise KeyError(converter_name)

            converter = converter_factory(*_parse_url_route_converter_args(m.group('args') or ''))
            variable = _UrlRouteVariable(name, converter)
            variables.append(variable)
            build_parts.append(variable)
            regex_parts.append('(' + converter.regex + ')')
            weight += converter.weight
            is_greedy = is_greedy or converter.is_greedy
            pos = m.end()

        if pos < len(segment):
            static = segment[pos:]
            regex_parts.append(re.escape(static))
            build_parts.append(static)
            weight -= len(static)

        if not variables:
            return segment, (segment,)

        if is_greedy and len(variables) != 1:
            raise ValueError(segment)

        return (
            _UrlRouteSegmentPattern(
                re.compile(r'\A' + ''.join(regex_parts) + r'\Z'),
                tuple(variables),
                weight,
                is_greedy=is_greedy,
            ),
            tuple(build_parts),
        )

    def _insert(self, compiled: _CompiledUrlRoute) -> None:
        node = self._root
        for idx, part in enumerate(compiled.parts):
            if isinstance(part, str):
                node = node.static.setdefault(part, _UrlRouteNode())
                continue

            if part.is_greedy:
                if idx != len(compiled.parts) - 1:
                    raise ValueError(compiled.route.pattern)
                node.greedy.append((part, compiled))
                node.greedy.sort(key=lambda e: (e[0].weight, e[1].order))
                return

            for existing, child in node.dynamic:
                if existing == part:
                    node = child
                    break
            else:
                child = _UrlRouteNode()
                node.dynamic.append((part, child))
                node.dynamic.sort(key=lambda e: e[0].weight)
                node = child

        node.routes.append(compiled)
        node.routes.sort(key=lambda r: r.order)

    def _match(
            self,
            path: str,
            *,
            method: ta.Optional[str],
    ) -> UrlRouteMatch:
        method = method.upper() if method is not None else None
        parts = _split_url_route_path(path)
        allowed_methods: set[str] = set()

        ret = self._match_node(
            self._root,
            parts,
            0,
            {},
            method,
            allowed_methods,
        )
        if ret is not None:
            return ret

        if allowed_methods:
            raise UrlRouteMethodNotAllowedError(path, method or '', frozenset(allowed_methods))
        raise UrlRouteNotFoundError(path)

    def _match_node(
            self,
            node: _UrlRouteNode,
            parts: ta.Sequence[str],
            idx: int,
            values: dict[str, ta.Any],
            method: ta.Optional[str],
            allowed_methods: set[str],
    ) -> ta.Optional[UrlRouteMatch]:
        if idx == len(parts):
            route_match = self._match_routes(node.routes, values, method, allowed_methods)
            if route_match is not None:
                return route_match

        if idx < len(parts):
            part = parts[idx]

            static_child = node.static.get(part)
            if static_child is not None:
                route_match = self._match_node(static_child, parts, idx + 1, values, method, allowed_methods)
                if route_match is not None:
                    return route_match

            for pattern, child in node.dynamic:
                next_values = self._match_pattern(pattern, part, values)
                if next_values is None:
                    continue
                route_match = self._match_node(child, parts, idx + 1, next_values, method, allowed_methods)
                if route_match is not None:
                    return route_match

            for pattern, compiled in node.greedy:
                remaining = '/'.join(parts[idx:])
                next_values = self._match_pattern(pattern, remaining, values)
                if next_values is None:
                    continue
                route_match = self._match_compiled_route(compiled, next_values, method, allowed_methods)
                if route_match is not None:
                    return route_match

        return None

    def _match_pattern(
            self,
            pattern: _UrlRouteSegmentPattern,
            part: str,
            values: ta.Mapping[str, ta.Any],
    ) -> ta.Optional[dict[str, ta.Any]]:
        m = pattern.regex.match(part)
        if m is None:
            return None

        next_values = dict(values)
        for variable, s in zip(pattern.variables, m.groups()):
            try:
                next_values[variable.name] = variable.converter.to_python(s)
            except ValueError:
                return None

        return next_values

    def _match_routes(
            self,
            routes: ta.Iterable[_CompiledUrlRoute],
            values: ta.Mapping[str, ta.Any],
            method: ta.Optional[str],
            allowed_methods: set[str],
    ) -> ta.Optional[UrlRouteMatch]:
        for compiled in routes:
            route_match = self._match_compiled_route(compiled, values, method, allowed_methods)
            if route_match is not None:
                return route_match
        return None

    def _match_compiled_route(
            self,
            compiled: _CompiledUrlRoute,
            values: ta.Mapping[str, ta.Any],
            method: ta.Optional[str],
            allowed_methods: set[str],
    ) -> ta.Optional[UrlRouteMatch]:
        if method is not None and compiled.methods is not None and method not in compiled.methods:
            allowed_methods.update(compiled.methods)
            return None

        route_values = dict(compiled.route.defaults or {})
        route_values.update(values)
        return UrlRouteMatch(compiled.route, route_values)

    def _try_build(
            self,
            compiled: _CompiledUrlRoute,
            values: ta.Mapping[str, ta.Any],
    ) -> ta.Optional[str]:
        parts = ['/']
        for part in compiled.build_parts:
            if isinstance(part, str):
                parts.append(_quote_url_route_static_part(part))
            else:
                if part.name not in values:
                    if compiled.route.defaults is not None and part.name in compiled.route.defaults:
                        value = compiled.route.defaults[part.name]
                    else:
                        return None
                else:
                    value = values[part.name]
                try:
                    parts.append(part.converter.to_url(value))
                except ValueError:
                    return None
        return ''.join(parts)

    @staticmethod
    def _alternate_slash_path(path: str) -> ta.Optional[str]:
        if path == '/':
            return None
        if path.endswith('/'):
            return path[:-1] or '/'
        return path + '/'

