import dataclasses as dc
import typing as ta

from . import xml


T = ta.TypeVar('T')


##


def symm_dct(*ks: T) -> ta.Mapping[T, T]:
    return {k: k for k in ks}


##


@dc.dataclass(frozen=True)
class Namespace:
    key: int
    case: str  # 'first-letter' | 'case-sensitive'
    text: str


parse_namespace = xml.ElementToObj(
    Namespace,
    xml.ElementToKwargs(
        attrs={
            'key': ('key', int),
            'case': 'case',
        },
        text='text',
    ),
)


#


@dc.dataclass(frozen=True)
class Namespaces:
    namespaces: ta.Sequence[Namespace] | None = None


parse_namespaces = xml.ElementToObj(
    Namespaces,
    xml.ElementToKwargs(
        list_children={
            'namespace': ('namespaces', parse_namespace),
        },
    ),
)


#


@dc.dataclass(frozen=True)
class SiteInfo:
    sitename: str
    dbname: str
    base: str
    generator: str
    case: str  # 'first-letter' | 'case-sensitive'
    namespaces: Namespaces


parse_site_info = xml.ElementToObj(
    SiteInfo,
    xml.ElementToKwargs(
        scalars=symm_dct(
            'sitename',
            'dbname',
            'base',
            'generator',
            'case',
        ),
        single_children={
            'namespaces': ('namespaces', parse_namespaces),
        },
    ),
)


#


@dc.dataclass(frozen=True)
class Redirect:
    title: str


parse_redirect = xml.ElementToObj(
    Redirect,
    xml.ElementToKwargs(
        attrs=symm_dct(
            'title',
        ),
    ),
)


#


@dc.dataclass(frozen=True)
class Contributor:
    username: str | None = None
    id: int | None = None
    ip: str | None = None
    deleted: bool | None = None


def _parse_deleted(s: str) -> bool:
    if s != 'deleted':
        raise ValueError(s)
    return True


parse_contributor = xml.ElementToObj(
    Contributor,
    xml.ElementToKwargs(
        attrs={
            'deleted': ('deleted', _parse_deleted),
        },
        scalars={
            **symm_dct(
                'username',
                'ip',
            ),
            'id': ('id', int),
        },
    ),
)


#


@dc.dataclass(frozen=True)
class RevisionText:
    bytes: int
    sha1: str
    text: str


parse_revision_text = xml.ElementToObj(
    RevisionText,
    xml.ElementToKwargs(
        attrs={
            'bytes': ('bytes', int),
            'sha1': 'sha1',
            'space': None,
        },
        text='text',
    ),
)


#


@dc.dataclass(frozen=True)
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


parse_revision = xml.ElementToObj(
    Revision,
    xml.ElementToKwargs(
        scalars={
            'id': ('id', int),
            'parentid': ('parentid', int),
            'origin': ('origin', int),
            'minor': ('minor', lambda _: True),
            **symm_dct(
                'timestamp',
                'comment',
                'model',
                'format',
                'sha1',
            ),
        },
        single_children={
            'text': ('text', parse_revision_text),
        },
        list_children={
            'contributor': ('contributors', parse_contributor),
        },
    ),
)


#


@dc.dataclass(frozen=True)
class Upload:
    timestamp: str | None = None
    contributor: str | None = None
    comment: str | None = None
    filename: str | None = None
    src: str | None = None
    size: str | None = None


#


@dc.dataclass(frozen=True)
class Page:
    title: str
    ns: int
    id: int
    redirect: Redirect | None = None
    restrictions: str | None = None
    revisions: ta.Sequence[Revision] | None = None
    uploads: ta.Sequence[Upload] | None = None


parse_page = xml.ElementToObj(
    Page,
    xml.ElementToKwargs(
        scalars={
            'ns': ('ns', int),
            'id': ('id', int),
            **symm_dct(
                'title',
                'restrictions',
            ),
        },
        single_children={
            'redirect': ('redirect', parse_redirect),
        },
        list_children={
            'revision': ('revisions', parse_revision),
        },
    ),
)


#


@dc.dataclass(frozen=True)
class MediaWiki:
    siteinfo: SiteInfo | None = None
    pages: ta.Sequence[Page] | None = None
