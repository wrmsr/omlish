"""
https://swagger.io/specification/
"""
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import marshal as msh
from ...formats import json


##


# https://swagger.io/specification/#security-requirement-object
SecurityRequirement: ta.TypeAlias = ta.Mapping[str, ta.Sequence[str]]


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class OauthFlow:
    """https://swagger.io/specification/#oauth-flow-object"""

    authorization_url: str
    token_url: str
    scopes: ta.Mapping[str, str]
    refresh_ur: str | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class OauthFlows:
    """https://swagger.io/specification/#oauth-flows-object"""

    implicit: OauthFlow | None = None
    password: OauthFlow | None = None
    client_credentials: OauthFlow | None = None
    authorization_code: OauthFlow | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
@msh.update_fields_metadata(['in_'], name='in')
class SecurityScheme:
    """https://swagger.io/specification/#security-scheme-object"""

    type: str
    scheme: str
    name: str | None = None
    in_: str | None = None
    description: str | None = None
    bearer_format: str | None = None
    flows: OauthFlows | None = None
    open_id_connect_url: str | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Xml:
    """https://swagger.io/specification/#xml-object"""

    name: str | None = None
    namespace: str | None = None
    prefix: str | None = None
    attribute: bool | None = None
    wrapped: bool | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Discriminator:
    """https://swagger.io/specification/#discriminator-object"""

    property_name: str
    mapping: ta.Mapping[str, str] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class Schema:
    """https://swagger.io/specification/#schema-object"""

    discriminator: Discriminator | None = None
    xml: Xml | None = None
    external_docs: ta.Optional['ExternalDocumentation'] = None
    example: ta.Any | None = None

    # FIXME: HACK: this is a jsonschema lol - these are just hacked on

    type: str | None = None
    format: str | None = None
    one_of: ta.Any = None
    all_of: ta.Any = None
    default: ta.Any = None
    enum: ta.Any = None
    items: ta.Any = None
    required: ta.Any = None
    properties: ta.Any = None
    description: str | None = None
    title: str | None = None
    deprecated: bool | None = None
    nullable: bool | None = None
    additional_properties: ta.Any = None

    #

    x: ta.Mapping[str, ta.Any] | None = None

    @dc.init
    def _check_x(self) -> None:
        for k in self.x or {}:
            check.arg(k.startswith('x-'))


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
@msh.update_fields_metadata(['ref'], name='$ref')
class Reference:
    """https://swagger.io/specification/#reference-object"""

    ref: str
    summary: str | None = None
    description: str | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Tag:
    """https://swagger.io/specification/#tag-object"""

    name: str
    description: str | None = None
    external_docs: ta.Optional['ExternalDocumentation'] = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
@msh.update_fields_metadata(['common'], embed=True, name='')
class Header:
    """https://swagger.io/specification/#header-object"""

    # TODO: marshal embedding, shared with Parameter
    common: 'ParameterCommon'


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Link:
    """https://swagger.io/specification/#link-object"""

    operation_ref: str | None = None
    operation_id: str | None = None
    parameters: ta.Mapping[str, ta.Any] | None = None
    request_body: ta.Any = None
    description: str | None = None
    server: ta.Optional['Server'] = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Example:
    """https://swagger.io/specification/#example-object"""

    summary: str | None = None
    description: str | None = None
    value: ta.Any | None = None
    external_value: str | None = None


# https://swagger.io/specification/#callback-object
Callback: ta.TypeAlias = ta.Mapping[str, ta.Union['PathItem', Reference]]


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Response:
    """https://swagger.io/specification/#response-object"""

    description: str
    headers: ta.Mapping[str, Header | Reference] | None = None
    content: ta.Mapping[str, 'MediaType'] | None = None
    links: ta.Mapping[str, Link | Reference] | None = None


# https://swagger.io/specification/#responses-object
Responses: ta.TypeAlias = ta.Mapping[str, Response | Reference]


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Encoding:
    """https://swagger.io/specification/#encoding-object"""

    content_type: str | None = None
    headers: ta.Mapping[str, Header | Reference] | None = None
    style: str | None = None
    explode: bool | None = None
    allow_reserved: bool | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class MediaType:
    """https://swagger.io/specification/#media-type-object"""

    schema: Schema | Reference | None = None
    example: ta.Any = None
    examples: ta.Mapping[str, Example | Reference] | None = None
    encoding: ta.Mapping[str, Encoding] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class RequestBody:
    """https://swagger.io/specification/#request-body-object"""

    content: ta.Mapping[str, MediaType]
    description: str | None = None
    required: bool | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class ParameterCommon:
    description: str | None = None
    required: bool | None = None
    deprecated: bool | None = None
    allow_empty_value: bool | None = None

    style: str | None = None
    explode: bool | None = None
    allow_reserved: bool | None = None
    schema: Schema | None = None
    example: ta.Any = None
    examples: ta.Mapping[str, Example | Reference] | None = None

    content: ta.Mapping[str, MediaType] | None = None

    # style: ta.Any = None
    matrix: ta.Any = None
    label: ta.Any = None
    form: ta.Any = None
    simple: ta.Any = None
    space_delimited: ta.Any = None
    pipe_delimited: ta.Any = None
    deep_object: ta.Any = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
@msh.update_fields_metadata(['in_'], name='in')
@msh.update_fields_metadata(['common'], embed=True, name='')
class Parameter:
    """https://swagger.io/specification/#parameter-object"""

    name: str
    in_: str

    common: ParameterCommon


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class ExternalDocumentation:
    """https://swagger.io/specification/#external-documentation-object"""

    url: str
    description: str | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class Operation:
    """https://swagger.io/specification/#operation-object"""

    tags: ta.Sequence[str] | None = None
    summary: str | None = None
    description: str | None = None
    external_docs: ExternalDocumentation | None = None
    operation_id: str | None = None
    parameters: ta.Sequence[Parameter | Reference] | None = None
    request_body: RequestBody | Reference | None = None
    responses: Responses | None = None
    callbacks: ta.Mapping[str, Callback | Reference] | None = None
    deprecated: bool | None = None
    security: ta.Sequence[SecurityRequirement] | None = None
    servers: ta.Sequence['Server'] | None = None

    #

    x: ta.Mapping[str, ta.Any] | None = None

    @dc.init
    def _check_x(self) -> None:
        for k in self.x or {}:
            check.arg(k.startswith('x-'))


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
@msh.update_fields_metadata(['ref'], name='$ref')
class PathItem:
    """https://swagger.io/specification/#path-item-object"""

    ref: str | None = None
    summary: str | None = None
    description: str | None = None
    get: Operation | None = None
    put: Operation | None = None
    post: Operation | None = None
    delete: Operation | None = None
    options: Operation | None = None
    head: Operation | None = None
    patch: Operation | None = None
    trace: Operation | None = None
    servers: ta.Sequence['Server'] | None = None
    parameters: ta.Sequence[Parameter | Reference] | None = None


# https://swagger.io/specification/#paths-object
Paths: ta.TypeAlias = ta.Mapping[str, PathItem]


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Components:
    """https://swagger.io/specification/#components-object"""

    schemas: ta.Mapping[str, Schema] | None = None
    responses: ta.Mapping[str, Response | Reference] | None = None
    parameters: ta.Mapping[str, Parameter | Reference] | None = None
    examples: ta.Mapping[str, Example | Reference] | None = None
    requestbodies: ta.Mapping[str, RequestBody | Reference] | None = None
    headers: ta.Mapping[str, Header | Reference] | None = None
    security_schemes: ta.Mapping[str, SecurityScheme | Reference] | None = None
    links: ta.Mapping[str, Link | Reference] | None = None
    callbacks: ta.Mapping[str, Callback | Reference] | None = None
    path_items: ta.Mapping[str, PathItem | Reference] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class ServerVariable:
    """https://swagger.io/specification/#server-variable-object"""

    default: str
    enum: ta.Sequence[str] | None = None
    description: str | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Server:
    """https://swagger.io/specification/#server-object"""

    url: str
    description: str | None = None
    variables: ta.Mapping[str, ServerVariable] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class License:
    """https://swagger.io/specification/#license-object"""

    name: str
    identifier: str | None = None
    url: str | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Contact:
    """https://swagger.io/specification/#contact-object"""

    name: str | None = None
    url: str | None = None
    email: str | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Info:
    """https://swagger.io/specification/#info-object"""

    title: str
    version: str
    summary: str | None = None
    description: str | None = None
    terms_of_service: str | None = None
    contact: Contact | None = None
    license: License | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class Openapi:
    """https://swagger.io/specification/#openapi-object"""

    openapi: str
    info: Info
    json_schema_dialect: str | None = None
    servers: ta.Sequence[Server] | None = None
    paths: Paths | None = None
    webhooks: ta.Mapping[str, PathItem | Reference] | None = None
    components: Components | None = None
    security: ta.Sequence[SecurityRequirement] | None = None
    tags: ta.Sequence[Tag] | None = None
    external_docs: ExternalDocumentation | None = None

    #

    x: ta.Mapping[str, ta.Any] | None = None

    @dc.init
    def _check_x(self) -> None:
        for k in self.x or {}:
            check.arg(k.startswith('x-'))


##


def _main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('schema_path')

    args = parser.parse_args()

    import yaml

    with open(args.schema_path) as f:
        doc = yaml.safe_load(f)

    api = msh.unmarshal(doc, Openapi)

    print(json.dumps_pretty(msh.marshal(api)))


if __name__ == '__main__':
    _main()
