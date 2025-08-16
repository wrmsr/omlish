# ruff: noqa: UP045
# @omlish-lite
import threading
import typing as ta

from ..lite.marshal import unmarshal_obj
from .loading import ManifestLoader


##


class GlobalManifestLoader:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    def __init_subclass__(cls, **kwargs):  # noqa
        raise TypeError

    ##

    _lock: ta.ClassVar[threading.RLock] = threading.RLock()

    _instance: ta.ClassVar[ta.Optional[ManifestLoader]] = None

    @classmethod
    def instance(cls) -> ManifestLoader:
        if (inst := cls._instance) is None:
            with cls._lock:
                if (inst := cls._instance) is None:
                    inst = cls._instance = ManifestLoader(**cls.default_kwargs())

        return inst

    @classmethod
    def initialize(cls, **kwargs: ta.Any) -> ManifestLoader:
        with cls._lock:
            if cls._instance is not None:
                raise Exception(f'{cls.__name__} already initialized')

            inst = cls._instance = ManifestLoader(**kwargs)

        return inst

    ##

    @classmethod
    def default_value_instantiator(cls, obj_cls: type, **kwargs: ta.Any) -> ta.Any:
        return unmarshal_obj(kwargs, obj_cls)

    @classmethod
    def default_kwargs(cls) -> ta.Mapping[str, ta.Any]:
        return dict(
            value_instantiator=cls.default_value_instantiator,
        )

    ##

    @classmethod
    def load(
            cls,
            *pkg_names: str,
            only: ta.Optional[ta.Iterable[type]] = None,
    ) -> ta.Sequence[ManifestLoader.LoadedManifest]:
        return cls.instance().load(
            *pkg_names,
            only=only,
        )
