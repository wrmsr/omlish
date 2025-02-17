import contextlib
import threading
import typing as ta

from .. import cached
from .. import check
from .. import lang
from .base import Codec
from .base import LazyLoadedCodec
from .standard import STANDARD_CODECS


if ta.TYPE_CHECKING:
    from ..manifests import load as manifest_load
else:
    manifest_load = lang.proxy_import('..manifests.load', __package__)


##


class CodecRegistry:
    def __init__(
            self,
            *,
            late_load_callbacks: ta.Iterable[ta.Callable[['CodecRegistry'], None]] | None = None,
    ) -> None:
        super().__init__()

        self._late_load_callbacks = late_load_callbacks

        self._lock = threading.RLock()
        self._by_name: dict[str, Codec | LazyLoadedCodec] = {}
        self._names_by_alias: dict[str, str] = {}
        self._names_by_cls: dict[type, list[str]] = {}

    def _late_load(self) -> None:
        if self._late_load_callbacks:
            for cb in self._late_load_callbacks:
                cb(self)
            self._late_load_callbacks = None

    @contextlib.contextmanager
    def _lock_and_load(self) -> ta.Iterator[None]:
        with self._lock:
            self._late_load()
            yield

    def _post_load(self, codec: Codec) -> None:
        for t in type(codec).__mro__:
            if t is not object:
                self._names_by_cls.setdefault(t, []).append(codec.name)

    def register(self, *codecs: Codec | LazyLoadedCodec) -> ta.Self:
        with self._lock:
            for codec in codecs:
                for n in {codec.name, *(codec.aliases or [])}:
                    if n in self._names_by_alias:
                        raise KeyError(n)

            for codec in codecs:
                self._by_name[codec.name] = codec
                for n in {codec.name, *(codec.aliases or [])}:
                    self._names_by_alias[n] = codec.name
                if isinstance(codec, Codec):
                    self._post_load(codec)

        return self

    def lookup(self, name_or_alias: str) -> Codec:
        with self._lock_and_load():
            name = self._names_by_alias[name_or_alias.replace('_', '-')]
            codec_or_lazy = self._by_name[name]

            if isinstance(codec_or_lazy, LazyLoadedCodec):
                codec = check.isinstance(codec_or_lazy.load(), Codec)
                self._by_name[name] = codec
                self._post_load(codec)
            else:
                codec = check.isinstance(codec_or_lazy, Codec)

            return codec

    def lookup_type(self, cls: type) -> list[Codec]:
        with self._lock_and_load():
            return [self.lookup(n) for n in self._names_by_cls.get(cls, [])]

    def all(self) -> frozenset[str]:
        with self._lock_and_load():
            return frozenset(self._by_name)


##


def _install_standard_codecs(registry: CodecRegistry) -> None:
    registry.register(*STANDARD_CODECS)


##


@cached.function
def _build_manifest_lazy_loaded_codecs() -> ta.Sequence[LazyLoadedCodec]:
    ldr = manifest_load.MANIFEST_LOADER
    pkgs = {__package__.split('.')[0], *ldr.discover_pkgs()}
    mns = ldr.load(*pkgs, only=[LazyLoadedCodec])
    return [m.value for m in mns]


def _install_manifest_lazy_loaded_codecs(registry: CodecRegistry) -> None:
    registry.register(*_build_manifest_lazy_loaded_codecs())


##


REGISTRY = CodecRegistry(
    late_load_callbacks=[
        _install_standard_codecs,
        _install_manifest_lazy_loaded_codecs,
    ],
)


def register(*codecs: Codec | LazyLoadedCodec) -> CodecRegistry:
    return REGISTRY.register(*codecs)


def lookup(name_or_alias: str) -> Codec:
    return REGISTRY.lookup(name_or_alias)


##


def encode(i: ta.Any, name: str, **kwargs: ta.Any) -> ta.Any:
    return lookup(name).new(**kwargs).encode(i)


def decode(o: ta.Any, name: str, **kwargs: ta.Any) -> ta.Any:
    return lookup(name).new(**kwargs).decode(o)
