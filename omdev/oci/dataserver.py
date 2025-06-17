# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.check import check

from ..dataserver.routes import DataServerRoute
from ..dataserver.targets import DataServerTarget
from .building import BuiltOciImageIndexRepository
from .building import OciRepositoryBuilder
from .datarefs import BytesOciDataRef
from .datarefs import FileOciDataRef
from .datarefs import open_oci_data_ref
from .media import OCI_MANIFEST_MEDIA_TYPES


##


def build_oci_repository_data_server_routes(
        repo_name: str,
        built_repo: BuiltOciImageIndexRepository,
) -> ta.List[DataServerRoute]:
    base_url_path = f'/v2/{repo_name}'

    repo_contents: ta.Dict[str, OciRepositoryBuilder.Blob] = {}

    repo_contents[f'{base_url_path}/manifests/latest'] = built_repo.blobs[built_repo.media_index_descriptor.digest]

    for blob in built_repo.blobs.values():
        repo_contents['/'.join([
            base_url_path,
            'manifests' if blob.media_type in OCI_MANIFEST_MEDIA_TYPES else 'blobs',
            blob.digest,
        ])] = blob

    #

    def build_blob_target(blob: OciRepositoryBuilder.Blob) -> ta.Optional[DataServerTarget]:  # noqa
        kw: dict = dict(
            content_type=check.non_empty_str(blob.media_type),
        )

        if isinstance(blob.data, BytesOciDataRef):
            return DataServerTarget.of(blob.data.data, **kw)

        elif isinstance(blob.data, FileOciDataRef):
            return DataServerTarget.of(file_path=blob.data.path, **kw)

        else:
            with open_oci_data_ref(blob.data) as f:
                data = f.read()

            return DataServerTarget.of(data, **kw)

    #

    return [
        DataServerRoute(
            paths=[path],
            target=target,
        )
        for path, blob in repo_contents.items()
        if (target := build_blob_target(blob)) is not None
    ]
