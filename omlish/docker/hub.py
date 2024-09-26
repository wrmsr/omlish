import typing as ta
import urllib.request

from .. import dataclasses as dc
from ..formats import json


@dc.dataclass(frozen=True)
class HubRepoInfo:
    repo: str
    tags: ta.Mapping[str, ta.Any]
    latest_manifests: ta.Mapping[str, ta.Any]


def get_hub_repo_info(
        repo: str,
        *,
        auth_url: str = 'https://auth.docker.io/',
        api_url: str = 'https://registry-1.docker.io/v2/',
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

    auth_url = auth_url.rstrip('/')
    api_url = api_url.rstrip('/')

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

    latest_mani_dct = req_json(
        f'{api_url}/{repo}/manifests/latest',
        headers={
            **req_hdrs,
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
        },
    )

    return HubRepoInfo(
        repo,
        tags_dct,
        latest_mani_dct,
    )
