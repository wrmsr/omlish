"""
TODO:
 - auth cmd

==

https://planspace.org/2013/01/13/upload-images-to-your-imgur-account/

https://api.imgur.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&response_type=pin

curl \
  -X POST \
  -F "client_id=YOUR_CLIENT_ID" \
  -F "client_secret=YOUR_CLIENT_SECRET" \
  -F "grant_type=pin" \
  -F "pin=YOUR_PIN" \
  https://api.imgur.com/oauth2/token

curl \
  -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image=@PATH_TO_YOUR_IMAGE_FILE" \
  https://api.imgur.com/3/upload
"""
import dataclasses as dc
import os.path
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.formats import json
from omlish.http import all as hu
from omlish.secrets.secrets import Secret

from .cli import CliModule
from .home.secrets import load_secrets


@dc.dataclass(frozen=True)
@msh.update_object_metadata(unknown_field='x')
class ImageUploadData:
    id: str
    deletehash: str  # noqa
    account_id: int
    account_url: str
    title: str
    description: str
    name: str
    type: str
    width: int
    height: int
    size: int
    views: int
    animated: bool
    has_sound: bool
    link: str
    tags: ta.Sequence[str]
    datetime: int
    mp4: str
    hls: str

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True)
class ImageUploadResponse:
    status: int
    success: bool
    data: ImageUploadData


DEFAULT_UPLOAD_IMAGE_URL = 'https://api.imgur.com/3/upload'


def upload_image(
        file_name: str,
        file_data: bytes,
        auth_key: Secret | str,
        *,
        url: str = DEFAULT_UPLOAD_IMAGE_URL,
        client: hu.HttpClient | None = None,
) -> ImageUploadResponse:
    me = hu.MultipartEncoder([
        hu.MultipartField(
            file_data,
            b'image',
            file_name.encode(),
            headers=[(hu.consts.HEADER_CONTENT_TYPE, hu.consts.CONTENT_TYPE_BYTES)],
        ),
    ])

    resp = hu.request(
        url,
        headers={
            hu.consts.HEADER_AUTH: hu.consts.format_bearer_auth_header(Secret.of(auth_key).reveal()),
            hu.consts.HEADER_CONTENT_TYPE: me.content_type().decode(),
        },
        data=me.content(),
        check=True,
        client=client,
    )

    return msh.unmarshal(json.loads(check.not_none(resp.data).decode('utf-8')), ImageUploadResponse)


def _main() -> None:
    from omlish.argparse import all as ap

    class Cli(ap.Cli):
        @ap.cmd(
            ap.arg('file'),
        )
        def upload(self) -> None:
            file = self.args.file
            file_name = os.path.basename(file)
            with open(file, 'rb') as f:
                file_data = f.read()

            resp = upload_image(
                file_name,
                file_data,
                load_secrets().get('imgur_client_access_token'),
            )

            print(resp.data.link)

    Cli()(exit=True)


# @omlish-manifest
_FOO_CLI_MODULE = CliModule('imgur', __name__)


if __name__ == '__main__':
    _main()
