# ruff: noqa: UP006 UP007
"""
TODO:
 - ~/.cache/omlish/interp/standalone/...
 - remove fallback
"""
# MIT License
#
# Copyright (c) 2023 Tushar Sadhwani
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
# https://github.com/tusharsadhwani/yen/blob/8d1bb0c1232c7b0159caefb1bf3a5348b93f7b43/src/yen/github.py
import json
import os.path
import platform
import re
import typing
import typing as ta
import urllib.error
import urllib.parse
import urllib.request

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.logs import log


class StandalonePythons:
    LAST_TAG_FOR_I686_LINUX = '118809599'  # tag name: "20230826"

    MACHINE_SUFFIX: ta.Mapping[str, ta.Mapping[str, ta.Any]] = {
        'Darwin': {
            'arm64': ['aarch64-apple-darwin-install_only.tar.gz'],
            'x86_64': ['x86_64-apple-darwin-install_only.tar.gz'],
        },
        'Linux': {
            'aarch64': {
                'glibc': ['aarch64-unknown-linux-gnu-install_only.tar.gz'],
                # musl doesn't exist
            },
            'x86_64': {
                'glibc': [
                    'x86_64_v3-unknown-linux-gnu-install_only.tar.gz',
                    'x86_64-unknown-linux-gnu-install_only.tar.gz',
                ],
                'musl': ['x86_64_v3-unknown-linux-musl-install_only.tar.gz'],
            },
            'i686': {
                'glibc': ['i686-unknown-linux-gnu-install_only.tar.gz'],
                # musl doesn't exist
            },
        },
        'Windows': {
            'AMD64': ['x86_64-pc-windows-msvc-shared-install_only.tar.gz'],
            'i686': ['i686-pc-windows-msvc-install_only.tar.gz'],
        },
    }

    GITHUB_API_RELEASES_URL = 'https://api.github.com/repos/indygreg/python-build-standalone/releases/'

    PYTHON_VERSION_REGEX = re.compile(r'cpython-(\d+\.\d+\.\d+)')

    class GitHubReleaseData(ta.TypedDict):
        id: int
        html_url: str
        assets: ta.List['StandalonePythons.GitHubAsset']

    class GitHubAsset(ta.TypedDict):
        browser_download_url: str

    def trim_github_release_data(self, release_data: ta.Dict[str, ta.Any]) -> GitHubReleaseData:
        return {
            'id': release_data['id'],
            'html_url': release_data['html_url'],
            'assets': [
                {'browser_download_url': asset['browser_download_url']}
                for asset in release_data['assets']
            ],
        }

    def fallback_release_data(self) -> GitHubReleaseData:
        """Returns the fallback release data, for when GitHub API gives an error."""

        log.warning('GitHub unreachable. Using fallback release data.')
        data_file = os.path.join(os.path.dirname(__file__), 'fallback_release_data.json')
        with open(data_file) as data:
            return typing.cast(StandalonePythons.GitHubReleaseData, json.load(data))

    class NotAvailableError(Exception):
        """Raised when the asked Python version is not available."""

    def get_latest_python_releases(self, is_linux_i686: bool) -> GitHubReleaseData:
        """Returns the list of python download links from the latest github release."""

        # They stopped shipping for 32 bit linux since after the 20230826 tag
        if is_linux_i686:
            data_file = os.path.join(os.path.dirname(__file__), 'linux_i686_release.json')
            with open(data_file) as data:
                return typing.cast(StandalonePythons.GitHubReleaseData, json.load(data))

        latest_release_url = urllib.parse.urljoin(self.GITHUB_API_RELEASES_URL, 'latest')
        try:
            with urllib.request.urlopen(latest_release_url) as response:  # noqa
                release_data = typing.cast(StandalonePythons.GitHubReleaseData, json.load(response))

        except urllib.error.URLError:
            release_data = self.fallback_release_data()

        return release_data

    @cached_nullary
    def list_pythons(self) -> ta.Mapping[str, str]:
        """Returns available python versions for your machine and their download links."""

        system, machine = platform.system(), platform.machine()
        download_link_suffixes = self.MACHINE_SUFFIX[system][machine]
        # linux suffixes are nested under glibc or musl builds
        if system == 'Linux':
            # fallback to musl if libc version is not found
            libc_version = platform.libc_ver()[0] or 'musl'
            download_link_suffixes = download_link_suffixes[libc_version]

        is_linux_i686 = system == 'Linux' and machine == 'i686'
        releases = self.get_latest_python_releases(is_linux_i686)
        python_releases = [asset['browser_download_url'] for asset in releases['assets']]

        available_python_links = [
            link
            # Suffixes are in order of preference.
            for download_link_suffix in download_link_suffixes
            for link in python_releases
            if link.endswith(download_link_suffix)
        ]

        python_versions: ta.Dict[str, str] = {}
        for link in available_python_links:
            match = self.PYTHON_VERSION_REGEX.search(link)
            python_version = check.not_none(match)[1]
            # Don't override already found versions, as they are in order of preference
            if python_version in python_versions:
                continue

            python_versions[python_version] = link

        sorted_python_versions = {
            version: python_versions[version]
            for version in sorted(
                python_versions,
                # sort by semver
                key=lambda version: [int(k) for k in version.split('.')],
                reverse=True,
            )
        }
        return sorted_python_versions

    def _parse_python_version(self, version: str) -> ta.Tuple[int, ...]:
        return tuple(int(k) for k in version.split('.'))

    def resolve_python_version(self, requested_version: ta.Optional[str]) -> ta.Tuple[str, str]:
        pythons = self.list_pythons()

        if requested_version is None:
            sorted_pythons = sorted(
                pythons.items(),
                key=lambda version_link: self._parse_python_version(version_link[0]),
                reverse=True,
            )
            latest_version, download_link = sorted_pythons[0]
            return latest_version, download_link

        for version, version_download_link in pythons.items():
            if version.startswith(requested_version):
                python_version = version
                download_link = version_download_link
                break
        else:
            raise StandalonePythons.NotAvailableError

        return python_version, download_link
