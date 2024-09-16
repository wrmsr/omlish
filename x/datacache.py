"""
TODO:
 - huggingface_hub
 - postprocessing?
  - unarchive
 - stupid little progress bars
"""
import datetime
import hashlib
import os.path
import tempfile
import typing as ta
import urllib.request

from omlish import __about__ as about
from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json


##


@cached.function
def _lib_revision() -> str | None:
    if (rev := about.__revision__) is not None:
        return rev

    try:
        from omdev.revisions import get_git_revision
    except ImportError:
        pass
    else:
        return get_git_revision()

    return None


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


@dc.dataclass(frozen=True)
class CacheDataManifest:
    spec: CacheDataSpec

    at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    lib_version: str = dc.field(default_factory=lambda: about.__version__)
    lib_revision: str = dc.field(default_factory=_lib_revision)

    VERSION: ta.ClassVar[int] = 0
    version: int = VERSION


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

    ##

    # retrieved = urllib.request.urlretrieve(spec.url)
    # print(retrieved)

    ##

    manifest = CacheDataManifest(spec)

    manifest_json = json.dumps_pretty(msh.marshal(manifest))
    print(manifest_json)


if __name__ == '__main__':
    _main()
