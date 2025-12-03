# Copyright (c) 2008-present The pip developers (see AUTHORS.txt file)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ~> https://github.com/pypa/pip/blob/a52069365063ea813fe3a3f8bac90397c9426d35/src/pip/_internal/commands/list.py (25.3)
import dataclasses as dc
import os.path
import ssl
import typing as ta

from omlish import cached
from omlish import check
from omlish.formats import json
from omlish.sync import ObjectPool


if ta.TYPE_CHECKING:
    from pip._internal.index.package_finder import PackageFinder  # noqa
    from pip._internal.metadata import BaseDistribution  # noqa
    from pip._internal.network.session import PipSession  # noqa
    from pip._vendor.packaging.version import Version  # noqa


##


@dc.dataclass(frozen=True, kw_only=True)
class IndexOptions:
    no_index: bool = False
    index_url: str | None = None
    extra_index_urls: ta.Sequence[str] | None = None

    def get_index_urls(self) -> list[str] | None:
        if self.no_index:
            return []

        index_urls: list[str] = []
        if (index_url := self.index_url) is None:
            from pip._internal.models.index import PyPI  # noqa
            index_url = PyPI.simple_url
        if index_url:
            index_urls.append(index_url)

        if (ext := self.extra_index_urls):
            index_urls.extend(ext)

        return index_urls or None


##


@dc.dataclass(frozen=True, kw_only=True)
class CacheOpts:
    no_cache: bool = False
    cache_dir: str | None = None

    def get_cache_dir(self) -> str | None:
        if self.no_cache:
            return None

        if (cache_dir := self.cache_dir) is None:
            from pip._internal.locations.base import USER_CACHE_DIR  # noqa
            cache_dir = USER_CACHE_DIR

        check.state(not cache_dir or os.path.isabs(cache_dir))
        return cache_dir


##


@dc.dataclass(frozen=True, kw_only=True)
class SessionOpts:
    DEFAULT_RETRIES: ta.ClassVar[int] = 5
    retries: int | None = DEFAULT_RETRIES

    DEFAULT_TIMEOUT: ta.ClassVar[int | None] = 15
    timeout: int | None = DEFAULT_TIMEOUT

    cert: str | None = None
    client_cert: str | None = None
    trusted_hosts: ta.Sequence[str] | None = None
    proxy: str | None = None

    keyring_provider: ta.Literal['auto', 'disabled', 'import', 'subprocess'] = 'auto'
    no_input: bool = False


def _create_truststore_ssl_context() -> ssl.SSLContext:
    from pip._vendor import certifi  # noqa
    from pip._vendor import truststore  # noqa

    ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(certifi.where())
    return ctx


def build_session(
        session_opts: SessionOpts = SessionOpts(),
        *,
        cache_opts: CacheOpts = CacheOpts(),
        index_opts: IndexOptions = IndexOptions(),
) -> 'PipSession':
    ssl_context = _create_truststore_ssl_context()

    from pip._internal.network.session import PipSession  # noqa
    session = PipSession(
        cache=os.path.join(cache_dir, 'http-v2') if (cache_dir := cache_opts.get_cache_dir()) else None,
        retries=session_opts.retries or 0,
        trusted_hosts=session_opts.trusted_hosts or [],
        index_urls=index_opts.get_index_urls(),
        ssl_context=ssl_context,
    )

    # Handle custom ca-bundles from the user
    if session_opts.cert:
        session.verify = session_opts.cert  # type: ignore[assignment]

    # Handle SSL client certificate
    if session_opts.client_cert:
        session.cert = session_opts.client_cert

    # Handle timeouts
    if session_opts.timeout:
        session.timeout = session_opts.timeout

    # Handle configured proxies
    if session_opts.proxy:
        session.proxies = {
            'http': session_opts.proxy,
            'https': session_opts.proxy,
        }
        session.trust_env = False
        session.pip_proxy = session_opts.proxy  # type: ignore[assignment]

    # Determine if we can prompt the user for authentication or not
    auth: ta.Any = session.auth
    auth.prompting = not session_opts.no_input
    auth.keyring_provider = session_opts.keyring_provider

    return session


##


def build_package_finder(
        session: 'PipSession',
        *,
        index_opts: IndexOptions = IndexOptions(),

        find_links: ta.Sequence[str] | None = None,
        pre: bool = False,
) -> 'PackageFinder':
    from pip._internal.models.search_scope import SearchScope  # noqa
    search_scope = SearchScope.create(
        find_links=list(find_links or []),
        index_urls=list(index_opts.get_index_urls() or []),
        no_index=index_opts.no_index,
    )

    from pip._internal.index.collector import LinkCollector  # noqa
    link_collector = LinkCollector(
        session=session,
        search_scope=search_scope,
    )

    # Pass allow_yanked=False to ignore yanked versions.
    from pip._internal.models.selection_prefs import SelectionPreferences  # noqa
    selection_prefs = SelectionPreferences(
        allow_yanked=False,
        allow_all_prereleases=pre,
    )

    from pip._internal.index.package_finder import PackageFinder  # noqa
    return PackageFinder.create(
        link_collector=link_collector,
        selection_prefs=selection_prefs,
    )


##


def get_dists(
        *,
        path: list[str] | None = None,
        local: bool = False,
        user: bool = False,
        editable: bool = False,
        include_editable: bool = True,
        skip: ta.Container | None = None,
) -> list['BaseDistribution']:
    from pip._internal.metadata import get_environment  # noqa
    return list(get_environment(path).iter_installed_distributions(
        local_only=local,
        user_only=user,
        editables_only=editable,
        include_editables=include_editable,
        skip=skip or set(),
    ))


##


@dc.dataclass(frozen=True, kw_only=True)
class DistLatestInfo:
    version: 'Version'
    filetype: str


def get_dist_latest_info(
        dist: 'BaseDistribution',
        finder: 'PackageFinder',
        *,
        pre: bool = False,
) -> DistLatestInfo | None:
    all_candidates = finder.find_all_candidates(dist.canonical_name)
    if not pre:
        # Remove prereleases
        all_candidates = [
            candidate
            for candidate in all_candidates
            if not candidate.version.is_prerelease
        ]

    evaluator = finder.make_candidate_evaluator(
        project_name=dist.canonical_name,
    )
    best_candidate = evaluator.sort_best_candidate(all_candidates)
    if best_candidate is None:
        return None

    remote_version = best_candidate.version
    if best_candidate.link.is_wheel:
        typ = 'wheel'
    else:
        typ = 'sdist'

    return DistLatestInfo(
        version=remote_version,
        filetype=typ,
    )


##


class Context:
    def __init__(self) -> None:
        super().__init__()

    #

    _session: ta.Optional['PipSession'] = None

    def session(self) -> 'PipSession':
        if self._session is None:
            self._session = build_session()
        return self._session

    #

    _finder: ta.Optional['PackageFinder'] = None

    def finder(self) -> 'PackageFinder':
        if self._finder is None:
            self._finder = build_package_finder(self.session())
        return self._finder

    #

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None


@dc.dataclass()
class Package:
    dist: 'BaseDistribution'

    @cached.function
    def version(self) -> str:
        from pip._vendor.packaging.version import InvalidVersion  # noqa
        try:
            return str(self.dist.version)
        except InvalidVersion:
            pass
        return self.dist.raw_version

    latest_info: DistLatestInfo | None = None


def _main() -> None:
    excludes: ta.Iterable[str] | None = None

    from pip._internal.utils.compat import stdlib_pkgs  # noqa
    skip = set(stdlib_pkgs)
    if excludes:
        from pip._vendor.packaging.utils import canonicalize_name  # noqa
        skip.update(canonicalize_name(n) for n in excludes)

    pkgs = [
        Package(dist)
        for dist in get_dists(
            skip=skip,
        )
    ]

    #

    context_pool: ObjectPool[Context] = ObjectPool(Context)

    def set_pkg_latest_info(pkg: Package) -> None:
        with context_pool.acquire() as ctx:
            pkg.latest_info = get_dist_latest_info(pkg.dist, ctx.finder())

    for pkg in pkgs:
        set_pkg_latest_info(pkg)

    context_pool.close()
    for ctx in context_pool.drain():
        ctx.close()

    #

    infos: list[dict[str, ta.Any]] = []

    for pkg in pkgs:
        if (latest_info := pkg.latest_info) is None or not (latest_info.version > pkg.dist.version):
            continue

        info = {
            'name': pkg.dist.raw_name,
            'version': pkg.version(),
            'location': pkg.dist.location or '',
            'installer': pkg.dist.installer,
            'latest_version': str(latest_info.version),
            'latest_filetype': latest_info.filetype,
        }

        if editable_project_location := pkg.dist.editable_project_location:
            info['editable_project_location'] = editable_project_location

        infos.append(info)

    print(json.dumps_pretty(infos))


if __name__ == '__main__':
    _main()
