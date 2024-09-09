import dataclasses as dc
import operator
import typing as ta

from omlish import marshal as msh


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class Namespace:
    key: int
    case: str  # 'first-letter' | 'case-sensitive'
    text: str


#


@dc.dataclass(frozen=True)
class Namespaces:
    namespaces: ta.Sequence[Namespace] | None = None


#


@dc.dataclass(frozen=True)
class SiteInfo:
    sitename: str
    dbname: str
    base: str
    generator: str
    case: str  # 'first-letter' | 'case-sensitive'
    namespaces: Namespaces


#


@dc.dataclass(frozen=True)
class Redirect:
    title: str


#


@dc.dataclass(frozen=True)
@msh.update_fields_metadata([
    'username',
    'id',
    'ip',
    'deleted',
], omit_if=operator.not_)
class Contributor:
    username: str | None = None
    id: int | None = None
    ip: str | None = None
    deleted: bool | None = None


#


@dc.dataclass(frozen=True)
class RevisionText:
    bytes: int
    sha1: str
    text: str


#


@dc.dataclass(frozen=True)
@msh.update_fields_metadata([
    'parentid',
    'timestamp',
    'contributors',
    'minor',
    'comment',
    'origin',
    'model',
    'format',
    'text',
    'sha1',
], omit_if=operator.not_)
class Revision:
    id: int
    parentid: int | None = None
    timestamp: str | None = None  # ISO8601
    contributors: ta.Sequence[Contributor] | None = None
    minor: bool = False
    comment: str | None = None
    origin: int | None = None
    model: str | None = None
    format: str | None = None
    text: RevisionText | None = None
    sha1: str | None = None


#


@dc.dataclass(frozen=True)
@msh.update_fields_metadata([
    'timestamp',
    'contributor',
    'comment',
    'filename',
    'src',
    'size',
], omit_if=operator.not_)
class Upload:
    timestamp: str | None = None
    contributor: str | None = None
    comment: str | None = None
    filename: str | None = None
    src: str | None = None
    size: str | None = None


#


@dc.dataclass(frozen=True)
@msh.update_fields_metadata([
    'redirect',
    'restrictions',
    'revisions',
    'uploads',
], omit_if=operator.not_)
class Page:
    title: str
    ns: int
    id: int
    redirect: Redirect | None = None
    restrictions: str | None = None
    revisions: ta.Sequence[Revision] | None = None
    uploads: ta.Sequence[Upload] | None = None


#


@dc.dataclass(frozen=True)
class MediaWiki:
    siteinfo: SiteInfo | None = None
    pages: ta.Sequence[Page] | None = None
