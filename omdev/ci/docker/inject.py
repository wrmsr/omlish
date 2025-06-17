# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .buildcaching import DockerBuildCaching
from .buildcaching import DockerBuildCachingImpl
from .cache import DockerCache
from .cache import DockerCacheImpl
from .cacheserved.cache import CacheServedDockerCache
from .imagepulling import DockerImagePulling
from .imagepulling import DockerImagePullingImpl
from .repositories import DockerImageRepositoryOpener
from .repositories import DockerImageRepositoryOpenerImpl


##


def bind_docker(
        *,
        build_caching_config: DockerBuildCachingImpl.Config,
        cache_served_docker_cache_config: ta.Optional[CacheServedDockerCache.Config] = None,
        image_pulling_config: DockerImagePullingImpl.Config = DockerImagePullingImpl.Config(),
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    #

    lst.extend([
        inj.bind(build_caching_config),
        inj.bind(DockerBuildCachingImpl, singleton=True),
        inj.bind(DockerBuildCaching, to_key=DockerBuildCachingImpl),
    ])

    #

    if cache_served_docker_cache_config is not None:
        lst.extend([
            inj.bind(DockerImageRepositoryOpenerImpl, singleton=True),
            inj.bind(DockerImageRepositoryOpener, to_key=DockerImageRepositoryOpenerImpl),

            inj.bind(cache_served_docker_cache_config),
            inj.bind(CacheServedDockerCache, singleton=True),
            inj.bind(DockerCache, to_key=CacheServedDockerCache),
        ])

    else:
        lst.extend([
            inj.bind(DockerCacheImpl, singleton=True),
            inj.bind(DockerCache, to_key=DockerCacheImpl),
        ])

    #

    lst.extend([
        inj.bind(image_pulling_config),
        inj.bind(DockerImagePullingImpl, singleton=True),
        inj.bind(DockerImagePulling, to_key=DockerImagePullingImpl),
    ])

    #

    return inj.as_bindings(*lst)
