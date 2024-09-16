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
import urllib.parse
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


#


def _maybe_sorted_strs(v: ta.Iterable[str] | None) -> ta.Sequence[str] | None:
    if v is None:
        return None
    return sorted(set(check.not_isinstance(v, str)))


@dc.dataclass(frozen=True)
class GitCacheDataSpec(CacheDataSpec):
    url: str

    branch: str | None = dc.field(default=None, kw_only=True)
    rev: str | None = dc.field(default=None, kw_only=True)

    subtrees: ta.Sequence[str] = dc.field(default=None, kw_only=True, coerce=_maybe_sorted_strs)


#


@dc.dataclass(frozen=True)
class HttpCacheDataSpec(CacheDataSpec):
    url: str = dc.field(validate=lambda u: bool(urllib.parse.urlparse(u)))
    file_name: str | None = None


#


def _repo_str(s: str) -> str:
    u, r = check.non_empty_str(s).split('/')
    check.non_empty_str(u)
    check.non_empty_str(r)
    return s


@dc.dataclass(frozen=True)
class GithubContentCacheDataSpec(CacheDataSpec):
    repo: str = dc.field(validate=_repo_str)
    rev: str
    paths: lang.SequenceNotStr[str]


##


@dc.dataclass(frozen=True)
class CacheDataManifest:
    spec: CacheDataSpec

    start_at: datetime.datetime = dc.field(kw_only=True)
    end_at: datetime.datetime = dc.field(kw_only=True)

    lib_version: str = dc.field(default_factory=lambda: about.__version__, kw_only=True)
    lib_revision: str = dc.field(default_factory=_lib_revision, kw_only=True)

    VERSION: ta.ClassVar[int] = 0
    version: int = dc.field(default=VERSION, kw_only=True)


##


@lang.cached_function
def _install_standard_marshalling() -> None:
    specs_poly = msh.polymorphism_from_subclasses(CacheDataSpec)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(specs_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(specs_poly)]


_install_standard_marshalling()


##


class DataCache:
    def __init__(self, base_dir: str) -> None:
        super().__init__()
        self._base_dir = base_dir

        self._items_dir = os.path.join(base_dir, 'items')

    def _fetch_into(self, spec: CacheDataSpec, data_dir: str) -> None:
        if isinstance(spec, HttpCacheDataSpec):
            if spec.file_name is not None:
                file_name = spec.file_name
            else:
                file_name = urllib.parse.urlparse(spec.url).path.split('/')[-1]

            urllib.request.urlretrieve(spec.url, os.path.join(data_dir, file_name))

        else:
            raise TypeError(spec)

    def get(self, spec: CacheDataSpec) -> str:
        os.makedirs(self._items_dir, exist_ok=True)

        #

        item_dir = os.path.join(self._items_dir, spec.digest)
        if os.path.isdir(item_dir):
            data_dir = os.path.join(item_dir, 'data')
            check.state(os.path.isdir(data_dir))
            return data_dir

        #

        tmp_dir = tempfile.mkdtemp()

        #

        data_dir = os.path.join(tmp_dir, 'data')
        os.mkdir(data_dir)

        start_at = lang.utcnow()
        self._fetch_into(spec, data_dir)
        end_at = lang.utcnow()

        #

        manifest = CacheDataManifest(
            spec,
            start_at=start_at,
            end_at=end_at,
        )
        manifest_json = json.dumps_pretty(msh.marshal(manifest))

        manifest_file = os.path.join(tmp_dir, 'manifest.json')
        with open(manifest_file, 'w') as f:
            f.write(manifest_json)

        ##

        os.rename(tmp_dir, item_dir)
        return os.path.join(item_dir, 'data')


##


def _main() -> None:
    cache_dir = tempfile.mkdtemp()
    print(f'{cache_dir=}')

    cache = DataCache(cache_dir)

    #

    for spec in [
        HttpCacheDataSpec('https://github.com/VanushVaswani/keras_mnistm/releases/download/1.0/keras_mnistm.pkl.gz'),
        GithubContentCacheDataSpec('karpathy/char-rnn', 'master', ['data/tinyshakespeare/input.txt'])
    ]:
        print(spec)
        print(cache.get(spec))


if __name__ == '__main__':
    _main()
