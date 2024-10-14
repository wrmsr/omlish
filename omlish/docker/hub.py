import typing as ta
import urllib.request

from .. import check
from .. import dataclasses as dc
from ..formats import json


@dc.dataclass(frozen=True)
class HubRepoInfo:
    repo: str
    tags: ta.Mapping[str, ta.Any]
    manifests: ta.Mapping[str, ta.Mapping[str, ta.Any]]


def get_hub_repo_info(
        repo: str,
        *,
        auth_url: str = 'https://auth.docker.io/',
        api_url: str = 'https://registry-1.docker.io/v2/',
        tags: ta.Iterable[str] | None = None,
) -> HubRepoInfo:
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
        tags = ['latest']

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

    tags_dct = req_json(
        f'{api_url}/{repo}/tags/list',
        headers=req_hdrs,
    )

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
