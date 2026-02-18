import functools
import typing as ta
import xml.etree.ElementTree as ET

from omlish import check
from omlish import dataclasses as dc

from .xml import append_xml_tail
from .xml import append_xml_val
from .xml import indent_xml
from .xml import render_xml_node_head


##


@functools.singledispatch
def make_xml(obj: ta.Any) -> ET.Element | None:
    raise TypeError(obj)


##


@dc.dataclass()
class Dependency:
    group_id: str
    artifact_id: str
    version: str

    _: dc.KW_ONLY

    type: str | None = None
    scope: str | None = None


@make_xml.register
def make_dependency_xml(obj: Dependency) -> ET.Element:
    el = ET.Element('dependency')

    append_xml_val(el, 'groupId', obj.group_id)
    append_xml_val(el, 'artifactId', obj.artifact_id)
    append_xml_val(el, 'version', obj.version)

    if obj.type is not None:
        append_xml_val(el, 'type', obj.type)
    if obj.scope is not None:
        append_xml_val(el, 'scope', obj.scope)

    return el


#


@dc.dataclass(kw_only=True)
class DependencyManagement:
    dependencies: list[Dependency] = dc.field(default_factory=list)


@make_xml.register
def make_dependency_management_xml(obj: DependencyManagement) -> ET.Element | None:
    if not obj.dependencies:
        return None

    el = ET.Element('dependencyManagement')

    for dep in obj.dependencies:
        if len(el):
            append_xml_tail(el[-1], '\n')
        el.append(make_dependency_xml(dep))

    return el


##


@dc.dataclass()
class Plugin:
    group_id: str | None
    artifact_id: str
    version: str

    _: dc.KW_ONLY

    extensions: bool | None = None

    executions: list[ta.Mapping[str, ta.Any]] | None = None

    configuration: dict[str, ta.Any] = dc.field(default_factory=dict)


@make_xml.register
def make_plugin_xml(obj: Plugin) -> ET.Element:
    el = ET.Element('plugin')

    if obj.group_id is not None:
        append_xml_val(el, 'groupId', obj.group_id)
    append_xml_val(el, 'artifactId', obj.artifact_id)
    append_xml_val(el, 'version', obj.version)

    if obj.extensions is not None:
        append_xml_val(el, 'extensions', 'true' if obj.extensions else 'false')

    if obj.executions:
        append_xml_val(ET.SubElement(el, 'executions'), 'execution', obj.executions)

    if obj.configuration:
        append_xml_val(el, 'configuration', obj.configuration)

    return el


#


@dc.dataclass(kw_only=True)
class PluginManagement:
    plugins: list[Plugin] = dc.field(default_factory=list)


@make_xml.register
def make_plugin_management_xml(obj: PluginManagement) -> ET.Element | None:
    if not obj.plugins:
        return None

    el = ET.Element('pluginManagement')

    for pg in obj.plugins:
        if len(el):
            append_xml_tail(el[-1], '\n')
        el.append(make_plugin_xml(pg))

    return el


#


@dc.dataclass(kw_only=True)
class Build:
    plugin_management: PluginManagement = dc.field(default_factory=lambda: PluginManagement())


@make_xml.register
def make_build_xml(obj: Build) -> ET.Element | None:
    if (pm_el := make_plugin_management_xml(obj.plugin_management)) is None:
        return None

    el = ET.Element('build')
    el.append(pm_el)
    return el


##


@dc.dataclass()
class Project:
    group_id: str
    artifact_id: str
    version: str

    name: str

    _: dc.KW_ONLY

    DEFAULT_MODEL_VERSION: ta.ClassVar[str] = '4.0.0'
    model_version: str = DEFAULT_MODEL_VERSION

    properties: ta.Mapping[str, str | int | float | bool] | None = None

    dependency_management: DependencyManagement = dc.field(default_factory=lambda: DependencyManagement())

    dependencies: list[Dependency] = dc.field(default_factory=list)

    build: Build = dc.field(default_factory=lambda: Build())


@make_xml.register
def make_project_xml(obj: Project) -> ET.Element:
    el = ET.Element('project')

    append_xml_val(el, 'modelVersion', obj.model_version, tail='\n')

    append_xml_val(el, 'groupId', obj.group_id)
    append_xml_val(el, 'artifactId', obj.artifact_id)
    append_xml_val(el, 'version', obj.version, tail='\n')

    append_xml_val(el, 'name', obj.name)

    if obj.properties:
        append_xml_tail(el[-1], '\n')
        append_xml_val(el, 'properties', obj.properties)

    if (dm_el := make_dependency_management_xml(obj.dependency_management)) is not None:
        append_xml_tail(el[-1], '\n')
        el.append(dm_el)

    if obj.dependencies:
        append_xml_tail(el[-1], '\n')
        deps_el = ET.SubElement(el, 'dependencies')

        for dep in obj.dependencies:
            if len(deps_el):
                append_xml_tail(deps_el[-1], '\n')
            deps_el.append(make_dependency_xml(dep))

    if (bld_el := make_build_xml(obj.build)) is not None:
        append_xml_tail(el[-1], '\n')
        el.append(bld_el)

    return el


def build_project_xml_attrs(prj: Project) -> ta.Mapping[str, str]:
    return {
        'xmlns': f'http://maven.apache.org/POM/{prj.model_version}',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': ' '.join([
            f'http://maven.apache.org/POM/{prj.model_version}',
            f'http://maven.apache.org/xsd/maven-{prj.model_version}.xsd',
        ]),
    }


##


def render_project_xml(prj: Project, *, indent: str = '  ') -> str:
    root = check.not_none(make_xml(prj))
    indent_xml(root, indent, keep_space_tails=True)
    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

    head_atts = build_project_xml_attrs(prj)
    prj_head = render_xml_node_head('project', head_atts, indent=indent)
    xml_str = xml_str.replace('<project>', prj_head, 1)

    return xml_str
