import difflib
import http
import typing as ta

from omlish import cached


if ta.TYPE_CHECKING:
    from .map import MapAdapter
    from .rules import Rule


##


class HttpException(Exception):  # noqa
    """
    The base class for all HTTP exceptions. This exception can be called as a WSGI application to render a default error
    page or you can catch the subclasses of it independently and render nicer error messages.
    """

    code: int | None = None
    description: str | None = None

    def __init__(
            self,
            description: str | None = None,
    ) -> None:
        super().__init__()

        if description is not None:
            self.description = description

    @property
    def name(self) -> str:
        """The status name."""

        if self.code is None:
            return 'Unknown Error'
        try:
            sc = http.HTTPStatus(self.code)
        except ValueError:
            return 'Unknown Error'
        else:
            return sc.phrase

    def __str__(self) -> str:
        code = self.code if self.code is not None else '???'
        return f'{code} {self.name}: {self.description}'

    def __repr__(self) -> str:
        code = self.code if self.code is not None else '???'
        return f"<{type(self).__name__} '{code}: {self.name}'>"


class BadRequest(HttpException):
    """
    *400* `Bad Request`

    Raise if the browser sends something to the application the application or server cannot handle.
    """

    code = 400
    description = 'The browser (or proxy) sent a request that this server could not understand.'


class NotFound(HttpException):
    """
    *404* `Not Found`

    Raise if a resource does not exist and never existed.
    """

    code = 404
    description = (
        'The requested URL was not found on the server. If you entered the URL manually please check your spelling and '
        'try again.'
    )


class MethodNotAllowed(HttpException):
    """
    *405* `Method Not Allowed`

    Raise if the server used a method the resource does not handle.  For example `POST` if the resource is view only.
    Especially useful for REST.

    The first argument for this exception should be a list of allowed methods. Strictly speaking the response would be
    invalid if you don't provide valid methods in the header which you can do with that list.
    """

    code = 405
    description = 'The method is not allowed for the requested URL.'

    def __init__(
            self,
            valid_methods: ta.Iterable[str] | None = None,
            description: str | None = None,
    ) -> None:
        """Takes an optional list of valid http methods starting with werkzeug 0.3 the list will be mandatory."""

        super().__init__(description=description)

        self.valid_methods = valid_methods


class BadHost(BadRequest):
    """Raised if the submitted host is badly formatted."""


class RoutingException(Exception):  # noqa
    """Special exceptions that require the application to redirect, notifying about missing urls, etc."""


class RequestRedirect(HttpException, RoutingException):
    """
    Raise if the map requests a redirect. This is for example the case if `strict_slashes` are activated and an url that
    requires a trailing slash.

    The attribute `new_url` contains the absolute destination url.
    """

    code = 308

    def __init__(self, new_url: str) -> None:
        super().__init__(new_url)

        self.new_url = new_url


class RequestPath(RoutingException):
    """Internal exception."""

    __slots__ = ('path_info',)

    def __init__(self, path_info: str) -> None:
        super().__init__()

        self.path_info = path_info


class RequestAliasRedirect(RoutingException):  # noqa: B903
    """This rule is an alias and wants to redirect to the canonical URL."""

    def __init__(self, matched_values: ta.Mapping[str, ta.Any], endpoint: ta.Any) -> None:
        super().__init__()

        self.matched_values = matched_values
        self.endpoint = endpoint


class BuildError(RoutingException, LookupError):
    """Raised if the build system cannot find a URL for an endpoint with the values provided."""

    def __init__(
            self,
            endpoint: ta.Any,
            values: ta.Mapping[str, ta.Any],
            method: str | None,
            adapter: ta.Optional['MapAdapter'] = None,
    ) -> None:
        super().__init__(endpoint, values, method)

        self.endpoint = endpoint
        self.values = values
        self.method = method
        self.adapter = adapter

    @cached.property
    def suggested(self) -> ta.Optional['Rule']:
        return self.closest_rule(self.adapter)

    def closest_rule(self, adapter: ta.Optional['MapAdapter']) -> ta.Optional['Rule']:
        def _score_rule(rule: 'Rule') -> float:
            return sum(
                [
                    0.98
                    * difflib.SequenceMatcher(
                        # endpoints can be any type, compare as strings
                        None,
                        str(rule.endpoint),
                        str(self.endpoint),
                    ).ratio(),
                    0.01 * bool(set(self.values or ()).issubset(rule.arguments)),
                    0.01 * bool(rule.methods and self.method in rule.methods),
                ],
            )

        if adapter and adapter.map._rules:  # noqa
            return max(adapter.map._rules, key=_score_rule)  # noqa

        return None

    def __str__(self) -> str:
        message = [f'Could not build url for endpoint {self.endpoint!r}']
        if self.method:
            message.append(f' ({self.method!r})')
        if self.values:
            message.append(f' with values {sorted(self.values)!r}')
        message.append('.')
        if self.suggested:
            if self.endpoint == self.suggested.endpoint:
                if (
                    self.method
                    and self.suggested.methods is not None
                    and self.method not in self.suggested.methods
                ):
                    message.append(
                        ' Did you mean to use methods'
                        f' {sorted(self.suggested.methods)!r}?',
                    )
                missing_values = self.suggested.arguments.union(
                    set(self.suggested.defaults or ()),
                ) - set(self.values.keys())
                if missing_values:
                    message.append(
                        f' Did you forget to specify values {sorted(missing_values)!r}?',
                    )
            else:
                message.append(f' Did you mean {self.suggested.endpoint!r} instead?')
        return ''.join(message)


class WebsocketMismatch(BadRequest):
    """
    The only matched rule is either a WebSocket and the request is HTTP, or the rule is HTTP and the request is a
    WebSocket.
    """


class NoMatch(Exception):  # noqa
    __slots__ = ('have_match_for', 'websocket_mismatch')

    def __init__(self, have_match_for: set[str], websocket_mismatch: bool) -> None:
        super().__init__()

        self.have_match_for = have_match_for
        self.websocket_mismatch = websocket_mismatch
