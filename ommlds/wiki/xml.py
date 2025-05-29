import typing as ta

from omlish import check

from . import models as mdl
from .utils import xml as xu


T = ta.TypeVar('T')


##


def symm_dct(*ks: T) -> ta.Mapping[T, T]:
    return {k: k for k in ks}


def parse_int(s: str | None) -> int:
    return int(check.non_empty_str(s))


##


parse_namespace = xu.ElementToObj(
    mdl.Namespace,
    xu.ElementToKwargs(
        attrs={
            'key': ('key', int),
            'case': 'case',
        },
        text='text',
    ),
)


parse_namespaces = xu.ElementToObj(
    mdl.Namespaces,
    xu.ElementToKwargs(
        list_children={
            'namespace': ('namespaces', parse_namespace),
        },
    ),
)


parse_site_info = xu.ElementToObj(
    mdl.SiteInfo,
    xu.ElementToKwargs(
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


parse_redirect = xu.ElementToObj(
    mdl.Redirect,
    xu.ElementToKwargs(
        attrs=symm_dct(
            'title',
        ),
    ),
)


def _parse_deleted(s: str) -> bool:
    if s != 'deleted':
        raise ValueError(s)
    return True


parse_contributor = xu.ElementToObj(
    mdl.Contributor,
    xu.ElementToKwargs(
        attrs={
            'deleted': ('deleted', _parse_deleted),
        },
        scalars={
            **symm_dct(
                'username',
                'ip',
            ),
            'id': ('id', parse_int),
        },
    ),
)


parse_revision_text = xu.ElementToObj(
    mdl.RevisionText,
    xu.ElementToKwargs(
        attrs={
            'bytes': ('bytes', int),
            'sha1': 'sha1',
            'space': None,
        },
        text='text',
    ),
)


parse_revision = xu.ElementToObj(
    mdl.Revision,
    xu.ElementToKwargs(
        scalars={
            'id': ('id', parse_int),
            'parentid': ('parentid', parse_int),
            'origin': ('origin', parse_int),
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


parse_page = xu.ElementToObj(
    mdl.Page,
    xu.ElementToKwargs(
        scalars={
            'ns': ('ns', parse_int),
            'id': ('id', parse_int),
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
