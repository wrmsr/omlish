import dataclasses as dc
import datetime
import typing as ta
import uuid

import pytest

from .... import inject as inj
from .... import lang
from .harness import PytestScope
from .harness import bind


##


@dc.dataclass(frozen=True)
class RunMetadata:
    request: pytest.FixtureRequest
    started_at: datetime.datetime = dc.field(default_factory=lang.localnow)
    uuid: uuid.UUID = dc.field(default_factory=uuid.uuid4)


#


@dc.dataclass(frozen=True)
class SessionRunMetadata(RunMetadata):
    pass


@dc.dataclass(frozen=True)
class PackageRunMetadata(RunMetadata):
    pass


@dc.dataclass(frozen=True)
class ModuleRunMetadata(RunMetadata):
    pass


@dc.dataclass(frozen=True)
class ClassRunMetadata(RunMetadata):
    pass


@dc.dataclass(frozen=True)
class FunctionRunMetadata(RunMetadata):
    pass


#


@bind('session', eager=True)
def _provide_session_metadata(
        request: ta.Annotated[pytest.FixtureRequest, inj.Tag(PytestScope.SESSION)],
) -> SessionRunMetadata:
    return SessionRunMetadata(request)


@bind('package', eager=True)
def _provide_package_metadata(
        request: ta.Annotated[pytest.FixtureRequest, inj.Tag(PytestScope.PACKAGE)],
) -> PackageRunMetadata:
    return PackageRunMetadata(request)


@bind('module', eager=True)
def _provide_module_metadata(
        request: ta.Annotated[pytest.FixtureRequest, inj.Tag(PytestScope.MODULE)],
) -> ModuleRunMetadata:
    return ModuleRunMetadata(request)


@bind('class', eager=True)
def _provide_class_metadata(
        request: ta.Annotated[pytest.FixtureRequest, inj.Tag(PytestScope.CLASS)],
) -> ClassRunMetadata:
    return ClassRunMetadata(request)


@bind('function', eager=True)
def _provide_function_metadata(
        request: ta.Annotated[pytest.FixtureRequest, inj.Tag(PytestScope.FUNCTION)],
) -> FunctionRunMetadata:
    return FunctionRunMetadata(request)
