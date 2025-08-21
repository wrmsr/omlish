"""
TODO:
 - read .idea/ for inference?
"""
import enum
import os.path
import typing as ta

from omlish.diag.pycharm import get_pycharm_version


##


class Ide(enum.Enum):
    PYCHARM = enum.auto()
    IDEA = enum.auto()
    CLION = enum.auto()
    WEBSTORM = enum.auto()
    GOLAND = enum.auto()


##


_INFER_FILE_NAME_SETS_BY_IDE: ta.Mapping[Ide, ta.AbstractSet[str]] = {

    Ide.PYCHARM: frozenset([
        'setup.py',
        'setup.cfg',
        'pyproject.toml',
        'requirements.txt',
        'Pipfile',
        'poetry.lock',
        '.python-version',
        'wsgi.py',
        'asgi.py',
        'manage.py',
    ]),

    Ide.IDEA: frozenset([
        'pom.xml',
        'mvnw',
        'build.gradle',
        'build.gradle.kts',
        'gradlew',
        'module-info.java',
        '.java-version',
    ]),

    Ide.CLION: frozenset([
        'CMakeLists.txt',
        'Cargo.toml',
        'config.h.in',
        'configure.ac',
        'configure.in',
        'rust-toolchain.toml',
        'vcpkg.json',
    ]),

    Ide.WEBSTORM: frozenset([
        'package.json',
        'package-lock.json',
    ]),

    Ide.GOLAND: frozenset([
        'go.mod',
        'go.sum',
    ]),

}


def infer_directory_ide(cwd: str | None) -> Ide | None:
    if cwd is None:
        cwd = os.getcwd()

    for i, fs in _INFER_FILE_NAME_SETS_BY_IDE.items():
        for f in fs:
            if os.path.exists(os.path.join(cwd, f)):
                return i

    return None


##


def get_ide_version(ide: Ide) -> str | None:
    if ide is Ide.PYCHARM:
        return get_pycharm_version()
    else:
        raise ValueError(ide)
