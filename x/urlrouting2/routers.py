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


class UrlRouteBuildError(Exception):
    pass


class UrlRouteConflictError(Exception):
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
class UrlRouteMatchMetadata:
    path: str
    matched_path: str
    query: str = ''


@dc.dataclass(frozen=True)
class UrlRouteMatch:
    route: UrlRoute
    values: UrlRouteValues
    metadata: UrlRouteMatchMetadata

    @property
    def endpoint(self) -> UrlRouteEndpoint:
        return self.route.endpoint

    @property
    def path(self) -> str:
        return self.metadata.path

    @property
    def matched_path(self) -> str:
        return self.metadata.matched_path


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
    match_key: ta.Tuple[ta.Any, ...]
    build_names: ta.AbstractSet[str]


@dc.dataclass()
class _UrlRouteNode:
    static: ta.MutableMapping[str, '_UrlRouteNode'] = dc.field(default_factory=dict)
    dynamic: list[ta.Tuple[_UrlRouteSegmentPattern, '_UrlRouteNode']] = dc.field(default_factory=list)
    greedy: list[ta.Tuple[_UrlRouteSegmentPattern, _CompiledUrlRoute]] = dc.field(default_factory=list)
    routes: list[_CompiledUrlRoute] = dc.field(default_factory=list)


##


class _UrlRouteArgParseError(ValueError):
    pass


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
        self._routes_by_match_key: dict[ta.Tuple[ta.Any, ...], list[_CompiledUrlRoute]] = {}
        self._route_build_names_by_name: dict[str, ta.AbstractSet[str]] = {}

        for route in routes:
            self.add(route)

    @property
    def config(self) -> UrlRouterConfig:
        return self._config

    def add(self, route: UrlRoute) -> None:
        compiled = self._compile_route(route, len(self._routes))
        self._check_conflicts(compiled)

        self._routes.append(compiled)
        self._routes_by_match_key.setdefault(compiled.match_key, []).append(compiled)
        if route.name is not None:
            self._routes_by_name_or_endpoint.setdefault(route.name, []).append(compiled)
            self._route_build_names_by_name[route.name] = compiled.build_names
        if route.endpoint is not None:
            self._routes_by_name_or_endpoint.setdefault(route.endpoint, []).append(compiled)
        self._insert(compiled)

    @staticmethod
    def _alternate_slash_path(path: str) -> ta.Optional[str]:
        if path == '/':
            return None
        if path.endswith('/'):
            return path[:-1] or '/'
        return path + '/'

    def match(
            self,
            path: str,
            *,
            method: ta.Optional[str] = None,
    ) -> UrlRouteMatch:
        split = urllib.parse.urlsplit(path)
        path = split.path or '/'
        original_path = path

        if self._config.merge_slashes:
            path = re.sub('/{2,}', '/', path)

        try:
            return self._match(path, original_path=original_path, query=split.query, method=method)
        except UrlRouteNotFoundError:
            pass

        alt_path = self._alternate_slash_path(path)
        if alt_path is not None:
            try:
                match = self._match(alt_path, original_path=original_path, query=split.query, method=method)
            except UrlRouteNotFoundError:
                pass
            else:
                slash_style = match.route.slash_style or self._config.slash_style
                if slash_style is UrlRouteSlashStyle.REDIRECT:
                    raise UrlRouteRedirectRequiredError(original_path, alt_path)
                if slash_style is UrlRouteSlashStyle.IGNORE:
                    return match

        raise UrlRouteNotFoundError(original_path)

    _URL_ROUTE_SENTINEL_METHOD: ta.ClassVar[str] = '__OMLISH_URL_ROUTER_METHOD_SENTINEL__'

    def allowed_methods(self, path: str) -> ta.AbstractSet[str]:
        try:
            self.match(path, method=self._URL_ROUTE_SENTINEL_METHOD)
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
            *,
            append_unknown: bool = False,
    ) -> str:
        values = values or {}
        build_error: ta.Optional[Exception] = None
        for compiled in self._routes_by_name_or_endpoint.get(name_or_endpoint, ()):
            try:
                built = self._try_build(compiled, values, append_unknown=append_unknown)
            except UrlRouteBuildError as e:
                build_error = e
            else:
                if built is not None:
                    return built

        if build_error is not None:
            raise build_error
        raise UrlRouteBuildError(name_or_endpoint)

    @staticmethod
    def _normalize_method_set(
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

    @staticmethod
    def _split_raw_path(path: str) -> list[str]:
        if not path.startswith('/'):
            raise ValueError(path)

        if path == '/':
            return []

        return path[1:].split('/')

    @staticmethod
    def _unquote_part(s: str) -> str:
        return urllib.parse.unquote(s, errors='strict')

    def _compile_route(self, route: UrlRoute, order: int) -> _CompiledUrlRoute:
        if not route.pattern.startswith('/'):
            raise ValueError(route.pattern)

        parts: list[_UrlRoutePart] = []
        build_parts: list[_UrlRouteBuildPart] = []
        match_key = []
        variable_names: set[str] = set()

        for raw_segment in self._split_raw_path(route.pattern):
            segment = self._unquote_part(raw_segment)
            pattern, segment_build_parts, segment_match_key, segment_variable_names = self._compile_segment(segment)
            duplicate_names = variable_names & segment_variable_names
            if duplicate_names:
                raise ValueError('duplicate route variables: ' + ', '.join(sorted(duplicate_names)))
            variable_names.update(segment_variable_names)
            parts.append(pattern)
            build_parts.extend(segment_build_parts)
            build_parts.append('/')
            match_key.append(segment_match_key)

        if build_parts:
            build_parts.pop()

        build_names = frozenset(p.name for p in build_parts if isinstance(p, _UrlRouteVariable))
        return _CompiledUrlRoute(
            route=route,
            parts=tuple(parts),
            build_parts=tuple(build_parts),
            methods=self._normalize_method_set(route.methods, add_head=self._config.add_head),
            order=order,
            match_key=tuple(match_key),
            build_names=build_names,
        )

    @staticmethod
    def _parse_arg_value(s: str) -> ta.Any:
        if s == 'True':
            return True
        if s == 'False':
            return False
        if s == 'None':
            return None
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
            return bytes(s[1:-1], 'utf-8').decode('unicode_escape')
        try:
            return int(s)
        except ValueError:
            pass
        try:
            return float(s)
        except ValueError:
            pass
        return s

    _URL_ROUTE_ARG_RE: ta.ClassVar[re.Pattern] = re.compile(
        r"""
        \s*
        (?:(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*)?
        (?P<value>
            True|False|None|
            -?\d+\.\d+|
            -?\d+|
            "(?:[^"\\]|\\.)*"|
            '(?:[^'\\]|\\.)*'|
            [^,\s]+)
        \s*(?:,|\Z)
        """,
        re.VERBOSE,
    )

    @classmethod
    def _parse_converter_args(cls, s: str) -> ta.Tuple[ta.Tuple[ta.Any, ...], dict[str, ta.Any]]:
        if not s:
            return (), {}

        args: list[ta.Any] = []
        kwargs: dict[str, ta.Any] = {}
        pos = 0
        while pos < len(s):
            m = cls._URL_ROUTE_ARG_RE.match(s, pos)
            if m is None:
                raise _UrlRouteArgParseError(s[pos:])
            value = UrlRouter._parse_arg_value(m.group('value'))
            name = m.group('name')
            if name is None:
                if kwargs:
                    raise _UrlRouteArgParseError(s[pos:])
                args.append(value)
            else:
                kwargs[name] = value
            pos = m.end()
        return tuple(args), kwargs

    _URL_ROUTE_VARIABLE_RE: ta.ClassVar[re.Pattern] = re.compile(
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

    def _compile_segment(
            self,
            segment: str,
    ) -> ta.Tuple[_UrlRoutePart, ta.Sequence[_UrlRouteBuildPart], ta.Any, ta.AbstractSet[str]]:
        pos = 0
        regex_parts = []
        variables = []
        build_parts: list[_UrlRouteBuildPart] = []
        match_key_parts: list[ta.Any] = []
        variable_names: set[str] = set()
        weight = 0
        is_greedy = False

        for m in self._URL_ROUTE_VARIABLE_RE.finditer(segment):
            if m.start() > pos:
                static = segment[pos:m.start()]
                regex_parts.append(re.escape(static))
                build_parts.append(static)
                match_key_parts.append(('s', static))
                weight -= len(static)

            name = m.group('name')
            if name in variable_names:
                raise ValueError('duplicate route variable: ' + name)
            variable_names.add(name)

            converter_name = m.group('converter') or 'str'
            converter_factory = self._converters.get(converter_name)
            if converter_factory is None:
                raise KeyError(converter_name)

            c_args, c_kwargs = self._parse_converter_args(m.group('args') or '')
            converter = converter_factory(*c_args, **c_kwargs)
            variable = _UrlRouteVariable(name, converter)
            variables.append(variable)
            build_parts.append(variable)
            regex_parts.append('(' + converter.regex + ')')
            match_key_parts.append(('v', converter.regex, converter.is_greedy))
            weight += converter.weight
            is_greedy = is_greedy or converter.is_greedy
            pos = m.end()

        if pos < len(segment):
            static = segment[pos:]
            regex_parts.append(re.escape(static))
            build_parts.append(static)
            match_key_parts.append(('s', static))
            weight -= len(static)

        if not variables:
            return segment, (segment,), ('s', segment), frozenset()

        if is_greedy and len(variables) != 1:
            raise ValueError(segment)

        regex = re.compile(r'\A' + ''.join(regex_parts) + r'\Z')
        return (
            _UrlRouteSegmentPattern(
                regex,
                tuple(variables),
                weight,
                is_greedy=is_greedy,
            ),
            tuple(build_parts),
            ('d', regex.pattern, tuple(match_key_parts)),
            frozenset(variable_names),
        )

    @staticmethod
    def _methods_overlap(
            a: ta.Optional[ta.AbstractSet[str]],
            b: ta.Optional[ta.AbstractSet[str]],
    ) -> bool:
        if a is None or b is None:
            return True
        return bool(a & b)

    def _check_conflicts(self, compiled: _CompiledUrlRoute) -> None:
        for other in self._routes_by_match_key.get(compiled.match_key, ()):
            if self._methods_overlap(other.methods, compiled.methods):
                raise UrlRouteConflictError(compiled.route.pattern)

        if compiled.route.name is not None:
            existing_build_names = self._route_build_names_by_name.get(compiled.route.name)
            if existing_build_names is not None and existing_build_names != compiled.build_names:
                raise UrlRouteConflictError(compiled.route.name)

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
            original_path: str,
            query: str,
            method: ta.Optional[str],
    ) -> UrlRouteMatch:
        method = method.upper() if method is not None else None
        parts = self._split_raw_path(path)
        allowed_methods: set[str] = set()
        metadata = UrlRouteMatchMetadata(
            path=original_path,
            matched_path=path,
            query=query,
        )

        ret = self._match_node(
            self._root,
            parts,
            0,
            {},
            method,
            allowed_methods,
            metadata,
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
            metadata: UrlRouteMatchMetadata,
    ) -> ta.Optional[UrlRouteMatch]:
        if idx == len(parts):
            route_match = self._match_routes(node.routes, values, method, allowed_methods, metadata)
            if route_match is not None:
                return route_match

        if idx < len(parts):
            raw_part = parts[idx]
            part = self._unquote_part(raw_part)

            static_child = node.static.get(part)
            if static_child is not None:
                route_match = self._match_node(static_child, parts, idx + 1, values, method, allowed_methods, metadata)
                if route_match is not None:
                    return route_match

            for pattern, child in node.dynamic:
                next_values = self._match_pattern(pattern, raw_part, values)
                if next_values is None:
                    continue
                route_match = self._match_node(child, parts, idx + 1, next_values, method, allowed_methods, metadata)
                if route_match is not None:
                    return route_match

            for pattern, compiled in node.greedy:
                remaining = '/'.join(parts[idx:])
                next_values = self._match_pattern(pattern, remaining, values)
                if next_values is None:
                    continue
                route_match = self._match_compiled_route(compiled, next_values, method, allowed_methods, metadata)
                if route_match is not None:
                    return route_match

        return None

    def _match_pattern(
            self,
            pattern: _UrlRouteSegmentPattern,
            raw_part: str,
            values: ta.Mapping[str, ta.Any],
    ) -> ta.Optional[dict[str, ta.Any]]:
        decoded_part = self._unquote_part(raw_part)
        candidate_parts = [raw_part]
        if decoded_part != raw_part:
            candidate_parts.append(decoded_part)

        for candidate_part in candidate_parts:
            m = pattern.regex.match(candidate_part)
            if m is None:
                continue

            next_values = dict(values)
            for variable, s in zip(pattern.variables, m.groups()):
                try:
                    next_values[variable.name] = variable.converter.to_python(self._unquote_part(s))
                except ValueError:
                    break
            else:
                return next_values

        return None

    def _match_routes(
            self,
            routes: ta.Iterable[_CompiledUrlRoute],
            values: ta.Mapping[str, ta.Any],
            method: ta.Optional[str],
            allowed_methods: set[str],
            metadata: UrlRouteMatchMetadata,
    ) -> ta.Optional[UrlRouteMatch]:
        for compiled in routes:
            route_match = self._match_compiled_route(compiled, values, method, allowed_methods, metadata)
            if route_match is not None:
                return route_match
        return None

    def _match_compiled_route(
            self,
            compiled: _CompiledUrlRoute,
            values: ta.Mapping[str, ta.Any],
            method: ta.Optional[str],
            allowed_methods: set[str],
            metadata: UrlRouteMatchMetadata,
    ) -> ta.Optional[UrlRouteMatch]:
        if method is not None and compiled.methods is not None and method not in compiled.methods:
            allowed_methods.update(compiled.methods)
            return None

        route_values = dict(compiled.route.defaults or {})
        route_values.update(values)
        return UrlRouteMatch(compiled.route, route_values, metadata)

    @staticmethod
    def _quote_static_part(s: str) -> str:
        return urllib.parse.quote(s, safe="!$&'()*+,/:;=@")

    @staticmethod
    def _query_encode(values: ta.Mapping[str, ta.Any]) -> str:
        items = []
        for k, v in values.items():
            if v is None:
                continue
            if isinstance(v, (list, tuple)):
                for e in v:
                    if e is not None:
                        items.append((k, e))
            else:
                items.append((k, v))
        return urllib.parse.urlencode(items, doseq=True, safe="!$'()*,/:;?@")

    def _try_build(
            self,
            compiled: _CompiledUrlRoute,
            values: ta.Mapping[str, ta.Any],
            *,
            append_unknown: bool,
    ) -> ta.Optional[str]:
        parts = ['/']
        consumed_names = set()
        for part in compiled.build_parts:
            if isinstance(part, str):
                parts.append(self._quote_static_part(part))
            else:
                consumed_names.add(part.name)
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

        unknown_values = {
            k: v
            for k, v in values.items()
            if k not in consumed_names and (compiled.route.defaults is None or k not in compiled.route.defaults)
        }
        if unknown_values:
            if not append_unknown:
                raise UrlRouteBuildError('unknown values: ' + ', '.join(sorted(unknown_values)))
            query = self._query_encode(unknown_values)
            if query:
                parts.extend(['?', query])

        return ''.join(parts)
