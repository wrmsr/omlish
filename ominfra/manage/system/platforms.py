import abc
import dataclasses as dc
import sys

from omlish.lite.cached import cached_nullary
from omlish.lite.logs import log
from omlish.os.linux import LinuxOsRelease


##


@dc.dataclass(frozen=True)
class Platform(abc.ABC):  # noqa
    pass


class LinuxPlatform(Platform, abc.ABC):
    pass


class UbuntuPlatform(LinuxPlatform):
    pass


class AmazonLinuxPlatform(LinuxPlatform):
    pass


class GenericLinuxPlatform(LinuxPlatform):
    pass


class DarwinPlatform(Platform):
    pass


class UnknownPlatform(Platform):
    pass


##


def _detect_system_platform() -> Platform:
    plat = sys.platform

    if plat == 'linux':
        if (osr := LinuxOsRelease.read()) is None:
            return GenericLinuxPlatform()

        if osr.id == 'amzn':
            return AmazonLinuxPlatform()

        elif osr.id == 'ubuntu':
            return UbuntuPlatform()

        else:
            return GenericLinuxPlatform()

    elif plat == 'darwin':
        return DarwinPlatform()

    else:
        return UnknownPlatform()


@cached_nullary
def detect_system_platform() -> Platform:
    platform = _detect_system_platform()
    log.info('Detected platform: %r', platform)
    return platform
