# ruff: noqa: UP006 UP045
# @omlish-lite
import os
import threading
import typing as ta

from ..lite.marshal import unmarshal_obj
from .loading import ManifestLoader


T = ta.TypeVar('T')


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
                    inst = cls._instance = ManifestLoader(cls.default_config())

        return inst

    @classmethod
    def initialize(cls, config: ta.Optional[ManifestLoader.Config] = None) -> ManifestLoader:
        with cls._lock:
            if cls._instance is not None:
                raise RuntimeError(f'{cls.__name__} already initialized')

            if config is None:
                config = cls.default_config()

            inst = cls._instance = ManifestLoader(config)

        return inst

    ##

    @classmethod
    def default_value_instantiator(cls, obj_cls: type, **kwargs: ta.Any) -> ta.Any:
        return unmarshal_obj(kwargs, obj_cls)

    @classmethod
    def default_config(cls) -> ManifestLoader.Config:
        return ManifestLoader.Config(
            discover_packages=True,
            discover_packages_fallback_scan_root_dirs=[os.getcwd()],

            value_instantiator=cls.default_value_instantiator,
        )

    ##

    @classmethod
    def load(
            cls,
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
            classes: ta.Optional[ta.Collection[type]] = None,
    ) -> ta.Sequence[ManifestLoader.LoadedManifest]:
        return cls.instance().load(
            packages=packages,
            classes=classes,
        )

    @classmethod
    def load_values(
            cls,
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
            classes: ta.Optional[ta.Collection[type]] = None,
    ) -> ta.Sequence[ta.Any]:
        return cls.instance().load_values(
            packages=packages,
            classes=classes,
        )

    @classmethod
    def load_values_of(
            cls,
            clz: ta.Type[T],
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
    ) -> ta.Sequence[T]:
        return cls.instance().load_values_of(
            clz,
            packages=packages,
        )
