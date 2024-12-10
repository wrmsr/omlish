import json
import time
import typing as ta

from omlish import check
from omlish.http import all as http
from omlish.http import jwt


DEFAULT_JWT_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'


def generate_gcp_jwt(
        creds_dct: ta.Mapping[str, ta.Any],
        *,
        issued_at: int | None = None,
        lifetime_s: int = 3600,
        scope: str = DEFAULT_JWT_SCOPE,
) -> str:
    return jwt.generate_jwt(
        issuer=creds_dct['client_email'],
        subject=creds_dct['client_email'],
        audience=creds_dct['token_uri'],
        issued_at=(issued_at := int(issued_at if issued_at is not None else time.time())),
        expires_at=issued_at + lifetime_s,
        scope=scope,
        key=creds_dct['private_key'],
        algorithm='RS256',
    )


def get_gcp_access_token(
        creds_dct: ta.Mapping[str, ta.Any],
        *,
        client: http.HttpClient | None = None,
) -> str:
    signed_jwt = generate_gcp_jwt(creds_dct)
    resp = http.request(
        creds_dct['token_uri'],
        'POST',
        data=jwt.build_get_token_body(signed_jwt).encode('utf-8'),
        headers={
            http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_FORM_URLENCODED,
        },
        client=client,
    )
    resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))
    return resp_dct['access_token']
