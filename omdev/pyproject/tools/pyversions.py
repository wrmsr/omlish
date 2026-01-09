# ruff: noqa: UP006 UP045
import dataclasses as dc
import json
import typing as ta
import urllib.request

from ..versions import VersionsFile


##


@dc.dataclass(frozen=True)
class PyVersion:
    name: str  # "Python 3.13.11",
    slug: str  # "python-31311"
    version: int  # 3
    is_published: bool
    is_latest: bool
    release_date: str  # "2025-12-05T19:24:49Z"
    pre_release: bool
    release_page: ta.Optional[str]
    release_notes_url: str  # "https://docs.python.org/release/3.13.11/whatsnew/changelog.html"
    show_on_download_page: bool
    resource_uri: str  # "https://www.python.org/api/v2/downloads/release/1083/"


PY_VERSIONS_URL = 'https://www.python.org/api/v2/downloads/release/?is_published=true'


def get_py_versions() -> ta.List[PyVersion]:
    with urllib.request.urlopen(PY_VERSIONS_URL) as r:  # noqa
        data = json.load(r)

    return [PyVersion(**dct) for dct in data]


##


def _main() -> None:
    print(get_py_versions())
    print(VersionsFile().pythons())


if __name__ == '__main__':
    _main()
