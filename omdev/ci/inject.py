# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .cache import DataCache
from .cache import DirectoryFileCache
from .cache import FileCache
from .cache import FileCacheDataCache
from .ci import Ci
from .docker.buildcaching import DockerBuildCachingImpl
from .docker.cacheserved.cache import CacheServedDockerCache
from .docker.imagepulling import DockerImagePullingImpl
from .docker.inject import bind_docker
from .github.inject import bind_github


##


def bind_ci(
        *,
        config: Ci.Config,

        directory_file_cache_config: ta.Optional[DirectoryFileCache.Config] = None,

        github: bool = False,

        cache_served_docker: bool = False,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [  # noqa
        inj.bind(config),
        inj.bind(Ci, singleton=True),
    ]

    lst.append(bind_docker(
        build_caching_config=DockerBuildCachingImpl.Config(
            service=config.service,

            always_build=config.always_build,
        ),

        cache_served_docker_cache_config=CacheServedDockerCache.Config(
            #
        ) if cache_served_docker else None,

        image_pulling_config=DockerImagePullingImpl.Config(
            always_pull=config.always_pull,
        ),
    ))

    if directory_file_cache_config is not None:
        lst.extend([
            inj.bind(directory_file_cache_config),
            inj.bind(DirectoryFileCache, singleton=True),
        ])

        if github:
            lst.append(bind_github())

        else:
            lst.extend([
                inj.bind(FileCache, to_key=DirectoryFileCache),

                inj.bind(FileCacheDataCache, singleton=True),
                inj.bind(DataCache, to_key=FileCacheDataCache),
            ])

    return inj.as_bindings(*lst)
