"""
TODO:
 - output 2 tables lol
 - min_time_since_prev_version
  - without this the min age is moot lol, can still catch a bad release at the same time of day just n days later
   - * at least show 'suggested', 'suggested age', 'latest', 'latest age', 'number of releases between the 2' *
  - how to handle non-linearity? new minor vers come out in parallel for diff major vers
   - trie?
 - find which reqs file + lineno to update
  - auto update

#

https://blog.yossarian.net/2025/11/21/We-should-all-be-using-dependency-cooldowns
https://news.ycombinator.com/item?id=46005111
"""
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
import datetime
import itertools
import os.path
import ssl
import typing as ta

from pip._internal.index.package_finder import LinkEvaluator  # noqa
from pip._internal.index.package_finder import PackageFinder  # noqa
from pip._internal.metadata import BaseDistribution  # noqa
from pip._internal.models.candidate import InstallationCandidate  # noqa
from pip._internal.models.link import Link  # noqa
from pip._internal.network.session import PipSession  # noqa
from pip._vendor.packaging.version import Version  # noqa

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish.concurrent import all as conc
from omlish.formats import json
from omlish.sync import ObjectPool


##


@cached.function
def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


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
) -> PipSession:
    ssl_context = _create_truststore_ssl_context()

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


class MyPackageFinder(PackageFinder):
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self._link_pypi_dict_by_hash: dict[str, dict[str, ta.Any]] = {}

    def get_link_pypi_dict(self, link: Link) -> dict[str, ta.Any] | None:
        if link.hash is None:
            return None
        return self._link_pypi_dict_by_hash.get(link.hash)

    def process_project_url(
            self,
            project_url: Link,
            link_evaluator: LinkEvaluator,
    ) -> list[InstallationCandidate]:
        index_response = self._link_collector.fetch_response(project_url)
        if index_response is None:
            return []

        page_links: list[Link] = []
        if index_response.content_type.lower().startswith('application/vnd.pypi.simple.v1+json'):
            data = json.loads(index_response.content)
            for file in data.get('files', []):
                link = Link.from_json(file, index_response.url)
                if link is None:
                    continue
                if link.hash is not None:
                    self._link_pypi_dict_by_hash[link.hash] = file
                page_links.append(link)

        else:
            from pip._internal.index.collector import parse_links  # noqa
            page_links = list(parse_links(index_response))

        from pip._internal.utils.logging import indent_log  # noqa
        with indent_log():
            package_links = self.evaluate_links(
                link_evaluator,
                links=page_links,
            )

        return package_links


def build_package_finder(
        session: PipSession,
        *,
        index_opts: IndexOptions = IndexOptions(),

        find_links: ta.Sequence[str] | None = None,
        pre: bool = False,
) -> MyPackageFinder:
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

    return check.isinstance(MyPackageFinder.create(
        link_collector=link_collector,
        selection_prefs=selection_prefs,
    ), MyPackageFinder)


##


def get_dists(
        *,
        path: list[str] | None = None,
        local: bool = False,
        user: bool = False,
        editable: bool = False,
        include_editable: bool = True,
        skip: ta.Container | None = None,
) -> list[BaseDistribution]:
    from pip._internal.metadata import get_environment  # noqa
    return list(get_environment(path).iter_installed_distributions(
        local_only=local,
        user_only=user,
        editables_only=editable,
        include_editables=include_editable,
        skip=skip or set(),
    ))


##


@dc.dataclass()
class Package:
    dist: BaseDistribution

    @cached.function
    def version(self) -> str:
        from pip._vendor.packaging.version import InvalidVersion  # noqa
        try:
            return str(self.dist.version)
        except InvalidVersion:
            pass
        return self.dist.raw_version

    @dc.dataclass(frozen=True)
    class Candidate:
        install: InstallationCandidate

        pypi_dict: dict[str, ta.Any] | None = None

        @cached.function
        def upload_time(self) -> datetime.datetime | None:
            if (ut := (self.pypi_dict or {}).get('upload-time')) is None:
                return None

            return datetime.datetime.fromisoformat(check.isinstance(ut, str))  # noqa

        @cached.property
        def version(self) -> Version:
            return self.install.version

        @cached.property
        def filetype(self) -> ta.Literal['wheel', 'sdist']:
            if self.install.link.is_wheel:
                return 'wheel'
            else:
                return 'sdist'

    unfiltered_candidates: ta.Sequence[Candidate] | None = None
    candidates: ta.Sequence[Candidate] | None = None

    latest_candidate: Candidate | None = None
    suggested_candidate: Candidate | None = None


def get_best_candidate(
        pkg: Package,
        finder: MyPackageFinder,
        candidates: ta.Sequence[Package.Candidate],
) -> Package.Candidate | None:
    candidates_by_install: ta.Mapping[InstallationCandidate, Package.Candidate] = col.make_map((
        (c.install, c)
        for c in candidates
    ), strict=True, identity=True)

    evaluator = finder.make_candidate_evaluator(
        project_name=pkg.dist.canonical_name,
    )
    best_install = evaluator.sort_best_candidate([c.install for c in candidates])
    if best_install is None:
        return None

    return candidates_by_install[best_install]


def set_package_finder_info(
        pkg: Package,
        finder: MyPackageFinder,
        *,
        pre: bool = False,
        max_uploaded_at: datetime.datetime | None = None,
        min_time_since_prev_version: datetime.timedelta | None = None,
) -> None:
    pkg.unfiltered_candidates = [
        Package.Candidate(
            c,
            finder.get_link_pypi_dict(c.link),
        )
        for c in finder.find_all_candidates(pkg.dist.canonical_name)
    ]

    #

    candidates = pkg.unfiltered_candidates

    if not pre:
        # Remove prereleases
        candidates = [
            c
            for c in candidates
            if not c.install.version.is_prerelease
        ]

    pkg.candidates = candidates

    #

    pkg.latest_candidate = get_best_candidate(pkg, finder, pkg.candidates)

    #

    suggested_candidates = candidates

    if min_time_since_prev_version is not None:
        # candidates_by_version = col.multi_map((c.install.version, c) for c in candidates)
        # uploaded_at_by_version = {
        #     v: min([c_ut for c in cs if (c_ut := c.upload_time()) is not None], default=None)
        #     for v, cs in candidates_by_version.items()
        # }
        raise NotImplementedError

    if max_uploaded_at is not None:
        suggested_candidates = [
            c
            for c in suggested_candidates
            if not (
                (c_dt := c.upload_time()) is not None and
                c_dt > max_uploaded_at
            )
        ]

    pkg.suggested_candidate = get_best_candidate(pkg, finder, suggested_candidates)


##


class Context:
    def __init__(self) -> None:
        super().__init__()

    #

    _session: PipSession | None = None

    def session(self) -> PipSession:
        if self._session is None:
            self._session = build_session()
        return self._session

    #

    _finder: MyPackageFinder | None = None

    def finder(self) -> MyPackageFinder:
        if self._finder is None:
            self._finder = build_package_finder(self.session())
        return self._finder

    #

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None


##


def human_round_td(td: datetime.timedelta) -> str:
    """Round a timedelta to its largest sensible unit."""

    seconds = td.total_seconds()

    # Define unit sizes in seconds
    units = [
        ('y', 365 * 24 * 3600),
        ('mo', 30 * 24 * 3600),
        ('w', 7 * 24 * 3600),
        ('d', 24 * 3600),
        ('h', 3600),
        ('m', 60),
        ('s', 1),
    ]

    for suffix, unit_seconds in units:
        value = seconds / unit_seconds
        if abs(value) >= 1:  # first unit where magnitude is >= 1
            return f'{round(value)}{suffix}'

    return '0s'


#


def format_for_json(
        pkgs: ta.Sequence[Package],
        *,
        now: datetime.datetime | None = None,
) -> list[dict[str, ta.Any]]:
    infos: list[dict[str, ta.Any]] = []

    for pkg in pkgs:
        latest = check.not_none(pkg.latest_candidate)
        suggested = check.not_none(pkg.suggested_candidate)

        info = {
            'name': pkg.dist.raw_name,
            'version': pkg.version(),
            'location': pkg.dist.location or '',
            'installer': pkg.dist.installer,
            'latest_version': str(latest.install.version),
            'latest_upload_time': lut.isoformat() if (lut := latest.upload_time()) is not None else None,
            'suggested_version': str(suggested.install.version),
            'suggested_upload_time': sut.isoformat() if (sut := suggested.upload_time()) is not None else None,
        }

        if editable_project_location := pkg.dist.editable_project_location:
            info['editable_project_location'] = editable_project_location

        infos.append(info)

    return infos


#


def format_for_columns(pkgs: ta.Sequence[Package]) -> tuple[list[list[str]], list[str]]:
    """Convert the package data into something usable by output_package_listing_columns."""

    header = [
        'Package',
        'Current',

        'Suggested',
        'Age',

        'Latest',
        'Age',
    ]

    # def wheel_build_tag(dist: BaseDistribution) -> str | None:
    #     try:
    #         wheel_file = dist.read_text('WHEEL')
    #     except FileNotFoundError:
    #         return None
    #     return email.parser.Parser().parsestr(wheel_file).get('Build')

    # build_tags = [wheel_build_tag(p.dist) for p in pkgs]
    # has_build_tags = any(build_tags)
    # if has_build_tags:
    #     header.append('Build')

    # has_editables = any(x.dist.editable for x in pkgs)
    # if has_editables:
    #     header.append('Editable project location')

    rows = []
    for pkg in pkgs:
        sc = check.not_none(pkg.suggested_candidate)
        lc = check.not_none(pkg.latest_candidate)

        row = [
            pkg.dist.raw_name,
            pkg.dist.raw_version,
        ]

        def add_c(c):
            if c is None:
                row.extend(['', ''])
                return

            row.append(str(c.version))

            if (l_ut := c.upload_time()) is not None:
                row.append(human_round_td(now_utc() - l_ut))
            else:
                row.append('')

        add_c(sc if sc.version != pkg.dist.version else None)
        add_c(lc if sc is not lc else None)

        # if has_build_tags:
        #     row.append(build_tags[i] or '')

        # if has_editables:
        #     row.append(pkg.dist.editable_project_location or '')

        rows.append(row)

    return rows, header


def _tabulate(
        rows: ta.Iterable[ta.Iterable[ta.Any]],
        *,
        sep: str = ' ',
) -> tuple[list[str], list[int]]:
    """
    Return a list of formatted rows and a list of column sizes.

    For example::

    >>> tabulate([['foobar', 2000], [0xdeadbeef]])
    (['foobar     2000', '3735928559'], [10, 4])
    """

    rows = [tuple(map(str, row)) for row in rows]
    sizes = [max(map(len, col)) for col in itertools.zip_longest(*rows, fillvalue='')]
    table = [sep.join(map(str.ljust, row, sizes)).rstrip() for row in rows]
    return table, sizes


def render_package_listing_columns(data: list[list[str]], header: list[str]) -> list[str]:
    # insert the header first: we need to know the size of column names
    if len(data) > 0:
        data.insert(0, header)

    pkg_strings, sizes = _tabulate(data, sep='  ')

    # Create and add a separator.
    if len(data) > 0:
        pkg_strings.insert(1, '  '.join('-' * x for x in sizes))

    return pkg_strings


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--exclude', action='append', dest='excludes')
    parser.add_argument('--min-age-h', type=float, default=24)
    parser.add_argument('-P', '--parallelism', type=int, default=3)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    max_uploaded_at: datetime.datetime | None = None
    if args.min_age_h is not None:
        max_uploaded_at = now_utc() - datetime.timedelta(hours=args.min_age_h)
    min_time_since_prev_version: datetime.timedelta | None = None  # datetime.timedelta(days=1)

    #

    from pip._internal.utils.compat import stdlib_pkgs  # noqa
    skip = set(stdlib_pkgs)
    if args.excludes:
        from pip._vendor.packaging.utils import canonicalize_name  # noqa
        skip.update(canonicalize_name(n) for n in args.excludes)

    pkgs = [
        Package(dist)
        for dist in get_dists(
            skip=skip,
        )
    ]

    #

    with ObjectPool[Context](Context).manage(lambda ctx: ctx.close()) as ctx_pool:
        with conc.new_executor(args.parallelism) as exe:
            def set_pkg_latest_info(pkg: Package) -> None:
                with ctx_pool.acquire() as ctx:  # noqa
                    set_package_finder_info(
                        pkg,
                        ctx.finder(),
                        max_uploaded_at=max_uploaded_at,
                        min_time_since_prev_version=min_time_since_prev_version,
                    )

            conc.wait_all_futures_or_raise([
                exe.submit(set_pkg_latest_info, pkg)
                for pkg in pkgs
            ])

    #

    outdated_pkgs = [
        pkg
        for pkg in pkgs
        if (li := pkg.latest_candidate) is not None
        and li.version > pkg.dist.version
    ]

    outdated_pkgs.sort(key=lambda x: x.dist.raw_name)

    #

    if args.json:
        print(json.dumps_pretty(format_for_json(outdated_pkgs)))

    else:
        # stable_pkgs, unstable_pkgs = col.partition(
        #     outdated_pkgs,
        #     lambda pkg: pkg.latest_candidate is pkg.suggested_candidate,
        # )

        print('\n'.join(render_package_listing_columns(*format_for_columns(outdated_pkgs))))


if __name__ == '__main__':
    _main()
