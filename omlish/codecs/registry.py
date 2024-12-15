import dataclasses as dc
import importlib
import threading
import typing as ta

from .. import cached
from .. import check
from .. import lang
from .base import Codec


if ta.TYPE_CHECKING:
    from ..manifests import load as manifest_load
else:
    manifest_load = lang.proxy_import('..manifests.load', __package__)


##


@dc.dataclass(frozen=True, kw_only=True)
class LazyLoadedCodec:
    mod_name: str
    attr_name: str
    name: str
    aliases: ta.Collection[str] | None = None


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
        with self._lock:
            name = self._names_by_alias[name_or_alias]
            codec_or_lazy = self._by_name[name]

            if isinstance(codec_or_lazy, LazyLoadedCodec):
                mod = importlib.import_module(codec_or_lazy.mod_name)
                codec = check.isinstance(getattr(mod, codec_or_lazy.attr_name), Codec)
                self._by_name = codec
                self._post_load(codec)
            else:
                codec = check.isinstance(codec_or_lazy, Codec)

            return codec

    def lookup_type(self, cls: type) -> list[Codec]:
        with self._lock:
            return [self.lookup(n) for n in self._names_by_cls.get(cls, [])]


##


@cached.function
def _build_manifest_lazy_loaded_codecs() -> ta.Sequence[LazyLoadedCodec]:
    raise NotImplementedError


def _install_manifest_lazy_loaded_codecs(registry: CodecRegistry) -> None:
    pass


##


REGISTRY = CodecRegistry(
    late_load_callbacks=[_install_manifest_lazy_loaded_codecs],
)

register = REGISTRY.register
lookup = REGISTRY.lookup
