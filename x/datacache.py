"""
TODO:
 - huggingface_hub
 - postprocessing?
  - unarchive
 - stupid little progress bars
"""
import hashlib
import os.path
import tempfile
import typing as ta
import urllib.request

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json


##


@dc.dataclass(frozen=True)
class CacheDataSpec(lang.Abstract, lang.Sealed):
    @cached.property
    def json(self) -> str:
        return json.dumps_compact(msh.marshal(self, CacheDataSpec))

    @cached.property
    def digest(self) -> str:
        return hashlib.md5(self.json.encode('utf-8')).hexdigest()  # noqa


def _maybe_sorted_strs(v: ta.Iterable[str] | None) -> ta.Sequence[str] | None:
    if v is None:
        return None
    return sorted(set(check.not_isinstance(v, str)))


@dc.dataclass(frozen=True)
class GitCacheDataSpec(CacheDataSpec):
    url: str

    branch: str | None = None
    rev: str | None = None

    subtrees: ta.Sequence[str] = dc.field(default=None, coerce=_maybe_sorted_strs)


@dc.dataclass(frozen=True)
class HttpCacheDataSpec(CacheDataSpec):
    url: str


@dc.dataclass(frozen=True)
class GithubContentCacheDataSpec(CacheDataSpec):
    repo: str
    rev: str
    paths: ta.Sequence[str]


##


@lang.cached_function
def _install_standard_marshalling() -> None:
    specs_poly = msh.polymorphism_from_subclasses(CacheDataSpec)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(specs_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(specs_poly)]


_install_standard_marshalling()


##


def _main() -> None:
    cache_dir = tempfile.mkdtemp()
    print(f'{cache_dir=}')

    spec = HttpCacheDataSpec('https://github.com/VanushVaswani/keras_mnistm/releases/download/1.0/keras_mnistm.pkl.gz')

    print(spec.json)
    print(spec.digest)


if __name__ == '__main__':
    _main()
