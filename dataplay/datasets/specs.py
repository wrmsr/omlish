"""
TODO:
 - import datasets
"""
import abc
import dataclasses as dc


@dc.dataclass(frozen=True)
class DatasetSpec(abc.ABC):
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
