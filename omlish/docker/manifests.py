"""
https://github.com/openshift/docker-distribution/blob/master/docs/spec/manifest-v2-2.md
"""
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh


##


SCHEMA_VERSION = 2


class MediaTypes(lang.Namespace):
    # schema1 (existing manifest format)
    MANIFEST_V1 = 'application/vnd.docker.distribution.manifest.v1+json'

    # New image manifest format (schemaVersion = 2)
    MANIFEST_V2 = 'application/vnd.docker.distribution.manifest.v2+json'

    # Manifest list, aka "fat manifest"
    MANIFEST_LIST = 'application/vnd.docker.distribution.manifest.list.v2+json'

    # Container config JSON
    CONTAINER_CONFIG = 'application/vnd.docker.container.image.v1+json'

    # "Layer", as a gzipped tar
    LAYER = 'application/vnd.docker.image.rootfs.diff.tar.gzip'

    # "Layer", as a gzipped tar that should never be pushed
    LAYER_NEVER_PUSH = 'application/vnd.docker.image.rootfs.foreign.diff.tar.gzip'

    # Plugin config JSON
    PLUGIN_CONFIG = 'application/vnd.docker.plugin.v1+json'


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
@msh.update_fields_metadata(['os_version'], name='os.version')
@msh.update_fields_metadata(['os_features'], name='os.features')
class Platform(lang.Final):
    # The architecture field specifies the CPU architecture, for example amd64 or ppc64le.
    architecture: str

    # The os field specifies the operating system, for example linux or windows.
    os: str

    # The optional os.version field specifies the operating system version, for example 10.0.10586.
    os_version: str | None = None

    # The optional os.features field specifies an array of strings, each listing a required OS feature (for example on
    # Windows win32k).
    os_features: ta.Sequence[ta.Any] | None = None

    # The optional variant field specifies a variant of the CPU, for example v6 to specify a particular CPU variant of
    # the ARM CPU.
    variant: str | None = None

    # The optional features field specifies an array of strings, each listing a required CPU feature (for example sse4
    # or aes).
    features: ta.Sequence[ta.Any] | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class Manifest(lang.Final):
    # The MIME type of the referenced object. This will generally be
    # application/vnd.docker.distribution.manifest.v2+json, but it could also be
    # application/vnd.docker.distribution.manifest.v1+json if the manifest list references a legacy schema-1 manifest.
    media_type: str

    # The size in bytes of the object. This field exists so that a client will have an expected size for the content
    # before validating. If the length of the retrieved content does not match the specified length, the content should
    # not be trusted.
    size: int

    # The digest of the content, as defined by the Registry V2 HTTP API Specification.
    digest: str

    # The platform object describes the platform which the image in the manifest runs on. A full list of valid operating
    # system and architecture values are listed in the Go language documentation for $GOOS and $GOARCH
    platform: Platform | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class ManifestList(lang.Final):
    # This field specifies the image manifest schema version as an integer. This schema uses the version 2.
    schema_version: int
    dc.validate(lambda self: self.schema_version == SCHEMA_VERSION)

    # The MIME type of the manifest list. This should be set to
    # application/vnd.docker.distribution.manifest.list.v2+json.
    media_type: str
    dc.validate(lambda self: self.media_type == MediaTypes.MANIFEST_LIST)

    # The manifests field contains a list of manifests for specific platforms.
    manifests: ta.Sequence[Manifest]

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class ImageManifest(lang.Final):
    # This field specifies the image manifest schema version as an integer. This schema uses version 2.
    schema_version: int
    dc.validate(lambda self: self.schema_version == SCHEMA_VERSION)

    # The MIME type of the manifest. This should be set to application/vnd.docker.distribution.manifest.v2+json.
    media_type: str
    dc.validate(lambda self: self.media_type == MediaTypes.MANIFEST_V2)

    @dc.dataclass(frozen=True)
    @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
    class Config(lang.Final):
        # The MIME type of the referenced object. This should generally be
        # application/vnd.docker.container.image.v1+json.
        media_type: str

        # The size in bytes of the object. This field exists so that a client will have an expected size for the content
        # before validating. If the length of the retrieved content does not match the specified length, the content
        # should not be trusted.
        size: int

        # The digest of the content, as defined by the Registry V2 HTTP API Specification.
        digest: str

        x: ta.Mapping[str, ta.Any] | None = None

    # The config field references a configuration object for a container, by digest. This configuration item is a JSON
    # blob that the runtime uses to set up the container. This new schema uses a tweaked version of this configuration
    # o allow image content-addressability on the daemon side.
    config: Config | None = None

    @dc.dataclass(frozen=True)
    @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
    class Layer(lang.Final):
        # The MIME type of the referenced object. This should generally be
        # application/vnd.docker.image.rootfs.diff.tar.gzip. Layers of type
        # application/vnd.docker.image.rootfs.foreign.diff.tar.gzip may be pulled from a remote location but they should
        # never be pushed.
        media_type: str

        # The size in bytes of the object. This field exists so that a client will have an expected size for the content
        # before validating. If the length of the retrieved content does not match the specified length, the content
        # should not be trusted.
        size: int

        # The digest of the content, as defined by the Registry V2 HTTP API Specification.
        digest: str

        # Provides a list of URLs from which the content may be fetched. Content must be verified against the digest and
        # size. This field is optional and uncommon.
        urls: ta.Sequence[str] | None = None

        x: ta.Mapping[str, ta.Any] | None = None

    # The layer list is ordered starting from the base image (opposite order of schema1).
    layers: ta.Sequence[Layer] | None = None

    x: ta.Mapping[str, ta.Any] | None = None
