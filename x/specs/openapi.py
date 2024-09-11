"""
https://swagger.io/specification/
"""
import dataclasses as dc
import os.path

import yaml

from omlish import marshal as msh


##


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class License:
    """https://swagger.io/specification/#license-object"""

    name: str | None = None
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
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Openapi:
    """https://swagger.io/specification/#openapi-object"""

    openapi: str
    info: Info


##


def _main():
    with open(os.path.join(os.path.dirname(__file__), '..', 'llm', 'openai.yaml')) as f:
        doc = yaml.safe_load(f)

    api = msh.unmarshal(doc, Openapi)
    print(api)


if __name__ == '__main__':
    _main()
