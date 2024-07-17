"""
TODO:
 - import datasets
"""
import dataclasses as dc

from omlish import lang


@dc.dataclass(frozen=True)
class DatasetSpec(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class GitDatasetSpec(DatasetSpec):
    repo_url: str

    branch_name: str | None = None
    rev: str | None = None

    repo_subtree: str | None = None


@dc.dataclass(frozen=True)
class HttpDatasetSpec(DatasetSpec):
    url: str
