# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import dataclasses as dc
import enum
import typing as ta

from ...lite.dataclasses import install_dataclass_filtered_repr


UrlRouteEndpoint = ta.Any  # ta.TypeAlias
UrlRouteValues = ta.Mapping[str, ta.Any]  # ta.TypeAlias


##


class UrlRouteSlashStyle(enum.Enum):
    STRICT = 'strict'
    REDIRECT = 'redirect'
    IGNORE = 'ignore'


##


class UrlRouteMatchError(Exception):
    pass


class UrlRouteBuildError(Exception):
    pass


class UrlRouteConflictError(Exception):
    pass


class UrlRouteArgParseError(ValueError):
    pass


@dc.dataclass()
class UrlRouteNotFoundError(UrlRouteMatchError):
    path: str


@dc.dataclass()
class UrlRouteMethodNotAllowedError(UrlRouteMatchError):
    path: str
    method: str
    allowed_methods: ta.AbstractSet[str]


@dc.dataclass()
class UrlRouteRedirectRequiredError(UrlRouteMatchError):
    path: str
    redirect_path: str


##


@install_dataclass_filtered_repr('omit_none')
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
