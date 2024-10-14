import typing as ta
import urllib.error
import urllib.request

from .. import check
from .. import dataclasses as dc
from ..formats import json


##


def _tag_sort_key(s: str) -> tuple:
    l = []
    for p in s.split('.'):
        v: ta.Any
        try:
            v = int(p)
        except ValueError:
            v = s
        l.append((not isinstance(v, int), v))
    return tuple(l)


DEFAULT_TAG_SUFFIX_DELIM = '-+'


def split_tag_suffix(
        tag: str,
        suffix_delim: ta.Iterable[str] = DEFAULT_TAG_SUFFIX_DELIM,
) -> tuple[str, str | None]:
    for d in suffix_delim:
        if d in tag:
            p, _, s = tag.partition(d)
            return p, s
    return tag, None


def select_latest_tag(
        tags: ta.Iterable[str],
        *,
        base: str | None = None,
        suffix: str | None = None,
        suffix_delim: ta.Iterable[str] = '-+',
) -> str:
    check.not_isinstance(tags, str)

    tags_by_sfx: dict[str | None, set[tuple[tuple, str]]] = {}
    for t in tags:
        p, s = split_tag_suffix(t, suffix_delim)
        tags_by_sfx.setdefault(s, set()).add((_tag_sort_key(p), t))

    if base is not None:
        bp, bs = split_tag_suffix(base, suffix_delim)
        if suffix is None:
            suffix = bs
        base_key = _tag_sort_key(bp)
    else:
        base_key = None

    sl = sorted(tags_by_sfx[suffix])

    if base_key is not None:
        sl = [(k, t) for k, t in sl if k[0] == base_key[0]]

    return sl[-1][1]


##


@dc.dataclass(frozen=True)
class HubRepoInfo:
    repo: str
    tags: ta.Sequence[str]
    manifests: ta.Mapping[str, ta.Mapping[str, ta.Any]]


def get_hub_repo_info(
        repo: str,
        *,
        auth_url: str = 'https://auth.docker.io/',
        api_url: str = 'https://registry-1.docker.io/v2/',
        tags: ta.Iterable[str] | None = None,
        handled_codes: ta.Container[int] | None = (401, 404),
) -> HubRepoInfo | None:
    """
    https://stackoverflow.com/a/39376254

    ==

    repo=library/nginx
    token=$(
        curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:${repo}:pull" \
        | jq -r '.token' \
    )
    curl -H "Authorization: Bearer $token" -s "https://registry-1.docker.io/v2/${repo}/tags/list" | jq
    curl \
        -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
        -H "Accept: application/vnd.docker.distribution.manifest.list.v2+json" \
        -H "Authorization: Bearer $token" \
        -s "https://registry-1.docker.io/v2/${repo}/manifests/latest" \
    | jq .
    """
    if tags is not None:
        check.not_isinstance(tags, str)
    else:
        tags = []

    auth_url = auth_url.rstrip('/')
    api_url = api_url.rstrip('/')

    if '/' not in repo:
        repo = '_/' + repo
    if repo.startswith('_/'):
        repo = 'library' + repo[1:]

    #

    def req_json(url: str, **kwargs: ta.Any) -> ta.Any:
        with urllib.request.urlopen(urllib.request.Request(url, **kwargs)) as resp:  # noqa
            return json.loads(resp.read().decode('utf-8'))

    #

    token_dct = req_json(f'{auth_url}/token?service=registry.docker.io&scope=repository:{repo}:pull')
    token = token_dct['token']

    req_hdrs = {'Authorization': f'Bearer {token}'}

    #

    try:
        tags_resp = req_json(
            f'{api_url}/{repo}/tags/list',
            headers=req_hdrs,
        )
    except urllib.error.HTTPError as ue:
        if ue.code in (handled_codes or ()):
            return None
        else:
            raise

    tags_dct = tags_resp.get('tags', {})

    manis = {}
    for tag in tags:
        mani = req_json(
            f'{api_url}/{repo}/manifests/latest',
            headers={
                **req_hdrs,
                'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
            },
        )
        manis[tag] = mani

    return HubRepoInfo(
        repo,
        tags_dct,
        manis,
    )
