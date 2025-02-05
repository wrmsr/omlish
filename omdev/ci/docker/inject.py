# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .buildcaching import DockerBuildCaching
from .buildcaching import DockerBuildCachingImpl
from .cache import DockerCache
from .cache import DockerCacheImpl
from .imagepulling import DockerImagePulling
from .imagepulling import DockerImagePullingImpl



##


def bind_docker(
    *,
    build_caching_config: DockerBuildCachingImpl.Config = DockerBuildCachingImpl.Config(),
    image_pulling_config: DockerImagePullingImpl.Config = DockerImagePullingImpl.Config(),
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bin(build_caching_config),
        inj.bind(DockerBuildCachingImpl, singleton=True),
        inj.bind(DockerBuildCaching, to_key=DockerBuildCachingImpl),

        inj.bind(DockerCacheImpl, singleton=True),
        inj.bind(DockerCache, to_key=DockerCacheImpl),

        inj.bind(image_pulling_config),
        inj.bind(DockerImagePullingImpl, singleton=True),
        inj.bind(DockerImagePulling, to_key=DockerImagePullingImpl),
    ]

    return inj.as_bindings(*lst)
