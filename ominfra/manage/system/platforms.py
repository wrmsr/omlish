import abc
import sys

from omlish.os.linux import LinuxOsRelease


##


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


def get_system_platform() -> Platform:
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
