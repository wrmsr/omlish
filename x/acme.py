#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.13"
# dependencies = []
# ///
# The MIT License (MIT)
#
# Copyright (c) 2025 Daniel Roesler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# https://github.com/diafygi/acme-tiny/blob/1b61d3001cb9c11380557ffebda5d358ce64375c/acme_tiny.py
#
# Copyright Daniel Roesler, under MIT license, included above.
"""
openssl genrsa 4096 > www/mydomain.party.key
openssl req -new -sha256 -key www/mydomain.party.key -subj "/CN=mydomain.party" > mydomain.party.csr

./acme.py \
  --account-key mydomain.party.key \
  --csr mydomain.party.csr \
  --acme-dir /www-data/.well-known/acme-challenge \
  --eab-kid "$ZEROSSL_EAB_KID" \
  --eab-hmac-key "$ZEROSSL_EAB_HMAC" \
  > mydomain.party.crt
"""
import argparse
import base64
import binascii
import hashlib
import hmac
import json
import logging
import os.path
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap
import time
import typing as ta
import urllib.request

from omlish import check


##


LETS_ENCRYPT_DIRECTORY_URL = 'https://acme-v02.api.letsencrypt.org/directory'
ZEROSSL_DIRECTORY_URL = 'https://acme.zerossl.com/v2/DV90'

DEFAULT_DIRECTORY_URL = ZEROSSL_DIRECTORY_URL


log = logging.getLogger(__name__)


def _b64_encode(b: bytes) -> str:
    """base64 encode for jose spec"""

    return base64.urlsafe_b64encode(b).decode('utf8').replace('=', '')


def _b64decode(b64_url_str: str) -> bytes:
    """base64url decode (ZeroSSL EAB HMAC key)"""

    # pad to a multiple of 4
    s = b64_url_str + '==='[: (4 - len(b64_url_str) % 4) % 4]
    return base64.urlsafe_b64decode(s.encode('utf8'))


def _cmd(
        cmd_list: ta.Sequence[str],
        *,
        stdin: ta.Any = None,
        cmd_input: bytes | None = None,
        err_msg: str = 'Command error',
) -> bytes | None:
    proc = subprocess.Popen(
        cmd_list,
        stdin=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = proc.communicate(cmd_input)

    if proc.returncode != 0:
        raise IOError(f'{err_msg}\n{err!r}')

    return out


class _DoRequestResult(ta.NamedTuple):
    data: ta.Any
    code: int
    headers: ta.Mapping[str, ta.Any]


def _do_request(
        url: str,
        *,
        data: bytes | None = None,
        err_msg: str = 'Request error',
        depth: int = 0,
) -> _DoRequestResult:
    try:
        resp = urllib.request.urlopen(urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/jose+json',
                'User-Agent': 'acme-tiny',
            },
        ))

        resp_data: ta.Any = resp.read().decode('utf8')
        code = resp.getcode()
        headers = resp.headers

    except IOError as e:
        resp_data = e.read().decode('utf8') if hasattr(e, 'read') else str(e)
        code = getattr(e, 'code', None)
        headers = {}

    try:
        resp_data = json.loads(resp_data)  # try to parse json results
    except ValueError:
        pass  # ignore json parsing errors

    if depth < 100 and code == 400 and resp_data['type'] == 'urn:ietf:params:acme:error:badNonce':
        raise IndexError(resp_data)  # allow 100 retrys for bad nonces

    if code not in [200, 201, 204]:
        raise ValueError(f'{err_msg}:\nUrl: {url}\nData: {data!r}\nResponse Code: {code}\nResponse: {resp_data!r}')

    return _DoRequestResult(resp_data, code, headers)


class _SignedRequestSender:
    def __init__(
            self,
            *,
            account_key: str,
            directory: ta.Mapping[str, ta.Any],
            acct_headers: ta.Mapping[str, ta.Any] | None = None,
            alg: str | None = None,
            jwk: ta.Mapping[str, ta.Any] | None = None,
    ) -> None:
        super().__init__()

        self._account_key = account_key
        self._directory = directory
        self._acct_headers = acct_headers
        self._alg = alg
        self._jwk = jwk

    def send_signed_request(
            self,
            url: str,
            payload: ta.Any | None = None,
            *,
            err_msg: str = 'Signed request error',
            depth: int = 0,
    ) -> _DoRequestResult:
        if payload is not None:
            payload_b64 = _b64_encode(json.dumps(payload).encode('utf8'))
        else:
            payload_b64 = ''

        new_nonce = _do_request(self._directory['newNonce'])[2]['Replay-Nonce']

        protected = {
            'url': url,
            'alg': self._alg,
            'nonce': new_nonce,
        }

        if self._acct_headers is None:
            protected['jwk'] = self._jwk
        else:
            protected['kid'] = self._acct_headers['Location']

        protected_b64 = _b64_encode(json.dumps(protected).encode('utf8'))
        protected_input = f'{protected_b64}.{payload_b64}'.encode('utf8')

        out = check.not_none(_cmd(
            [
                'openssl',
                'dgst',
                '-sha256',
                '-sign', self._account_key,
            ],
            stdin=subprocess.PIPE,
            cmd_input=protected_input,
            err_msg='OpenSSL Error',
        ))

        data = json.dumps({
            'protected': protected_b64,
            'payload': payload_b64,
            'signature': _b64_encode(out),
        })

        try:
            return _do_request(
                url,
                data=data.encode('utf8'),
                err_msg=err_msg,
                depth=depth,
            )

        except IndexError:  # retry bad nonces (they raise IndexError)
            return self.send_signed_request(
                url,
                payload,
                err_msg=err_msg,
                depth=depth + 1,
            )

    def poll_until_not(
            self,
            url: str,
            pending_statuses: ta.Container[str],
            *,
            err_msg: str = 'Poll request error',
    ) -> ta.Any:
        result = None
        t0 = time.time()

        while result is None or result['status'] in pending_statuses:
            check.state(time.time() - t0 < 3600, 'Polling timeout')  # 1 hour timeout

            time.sleep(0 if result is None else 2)

            result = self.send_signed_request(
                url,
                err_msg=err_msg,
            ).data

        return result


def get_crt(
        account_key: str,
        csr: str,
        acme_dir: str,
        *,
        disable_check: bool = False,
        directory_url: str = DEFAULT_DIRECTORY_URL,
        contact: ta.Sequence[str] | None = None,
        check_port: int | None = None,
        eab_kid: str | None = None,
        eab_hmac_key: str | None = None,
) -> ta.Any:
    # parse account key to get public key

    log.info('Parsing account key...')

    out = check.not_none(_cmd(
        [
            'openssl',
            'rsa',
            '-in', account_key,
            '-noout',
            '-text',
        ],
        err_msg='OpenSSL Error',
    ))

    pub_hex, pub_exp = check.not_none(re.search(
        r'modulus:\s+?00:([a-f0-9:\s]+?)\npublicExponent: ([0-9]+)',
        out.decode('utf8'),
        re.MULTILINE | re.DOTALL,
    )).groups()

    pub_exp = f'{int(pub_exp):x}'
    pub_exp = f'0{pub_exp}' if len(pub_exp) % 2 else pub_exp

    alg = 'RS256'
    jwk = {
        'e': _b64_encode(binascii.unhexlify(pub_exp.encode('utf-8'))),
        'kty': 'RSA',
        'n': _b64_encode(binascii.unhexlify(re.sub(r'(\s|:)', '', pub_hex).encode('utf-8'))),
    }

    account_key_json = json.dumps(jwk, sort_keys=True, separators=(',', ':'))
    thumbprint = _b64_encode(hashlib.sha256(account_key_json.encode('utf8')).digest())

    # find domains

    log.info('Parsing CSR...')

    out = check.not_none(_cmd(
        [
            'openssl',
            'req',
            '-in', csr,
            '-noout',
            '-text',
        ],
        err_msg=f'Error loading {csr}',
    ))

    domains: set[str] = set()

    common_name = re.search(r'Subject:.*? CN\s?=\s?([^\s,;/]+)', out.decode('utf8'))
    if common_name is not None:
        domains.add(common_name.group(1))

    subject_alt_names = re.search(
        r'X509v3 Subject Alternative Name: (?:critical)?\n +([^\n]+)\n',
        out.decode('utf8'),
        re.MULTILINE | re.DOTALL,
    )

    if subject_alt_names is not None:
        for san in subject_alt_names.group(1).split(', '):
            if san.startswith('DNS:'):
                domains.add(san[4:])

    log.info(f'Found domains: {", ".join(domains)}')

    # get the ACME directory of urls

    log.info('Getting directory...')

    directory = _do_request(directory_url, err_msg='Error getting directory').data

    log.info('Directory found!')

    # create account, update contact details (if any), and set the global key identifier

    log.info('Registering account...')

    reg_payload: dict[str, ta.Any]
    if contact is None:
        reg_payload = {'termsOfServiceAgreed': True}
    else:
        reg_payload = {'termsOfServiceAgreed': True, 'contact': contact}

    # If EAB credentials were provided (e.g. for ZeroSSL), add externalAccountBinding
    if eab_kid and eab_hmac_key:
        # JWS protected header for EAB
        eab_protected = {
            'alg': 'HS256',
            'kid': eab_kid,
            'url': directory['newAccount'],
        }

        # Payload is the account key JWK
        # account_key_json is the canonical JSON string of jwk we already computed
        eab_protected_b64 = _b64_encode(json.dumps(eab_protected).encode('utf8'))
        eab_payload_b64 = _b64_encode(account_key_json.encode('utf8'))

        mac_key = _b64decode(eab_hmac_key)
        mac_input = f'{eab_protected_b64}.{eab_payload_b64}'.encode('utf8')
        mac = hmac.new(mac_key, mac_input, hashlib.sha256)
        eab_signature_b64 = _b64_encode(mac.digest())

        reg_payload['externalAccountBinding'] = {
            'protected': eab_protected_b64,
            'payload': eab_payload_b64,
            'signature': eab_signature_b64,
        }

    acct_headers = None

    def ssr() -> _SignedRequestSender:
        return _SignedRequestSender(
            account_key=account_key,
            directory=directory,
            acct_headers=acct_headers,
            alg=alg,
            jwk=jwk,
        )

    account, code, acct_headers = ssr().send_signed_request(
        directory['newAccount'],
        reg_payload,
        err_msg='Error registering',
    )

    log.info(
        f'{"Registered!" if code == 201 else "Already registered!"} '
        f'Account ID: {acct_headers["Location"]}',
    )

    if contact is not None:
        account = ssr().send_signed_request(
            acct_headers['Location'],
            {
                'contact': contact,
            },
            err_msg='Error updating contact details',
        ).data

        log.info('Updated contact details:\n{0}'.format('\n'.join(account.get('contact') or [])))

    # create a new order

    log.info('Creating new order...')

    order, _, order_headers = ssr().send_signed_request(
        directory['newOrder'],
        {
            'identifiers': [
                {
                    'type': 'dns',
                    'value': d,
                }
                for d in domains
            ],
        },
        err_msg='Error creating new order',
    )

    log.info('Order created!')

    # get the authorizations that need to be completed
    for auth_url in order['authorizations']:
        authorization = ssr().send_signed_request(
            auth_url,
            None,
            err_msg='Error getting challenges',
        ).data

        domain = authorization['identifier']['value']

        # skip if already valid
        if authorization['status'] == 'valid':
            log.info(f'Already verified: {domain}, skipping...')
            continue

        log.info(f'Verifying {domain}...')

        # find the http-01 challenge and write the challenge file
        challenge = [c for c in authorization['challenges'] if c['type'] == 'http-01'][0]

        token = re.sub(r'[^A-Za-z0-9_\-]', '_', challenge['token'])

        key_authorization = f'{token}.{thumbprint}'

        tmp_dir = tempfile.mkdtemp()
        tmp_wellknown_path = os.path.join(tmp_dir, token)
        with open(tmp_wellknown_path, 'w') as tmp_wellknown_file:
            tmp_wellknown_file.write(key_authorization)

        wellknown_path = os.path.join(acme_dir, token)

        cp_wellknown_sh = (
            f'cp {shlex.quote(tmp_wellknown_path)} {shlex.quote(wellknown_path)} && '
            f'chown www-data:www-data {shlex.quote(wellknown_path)}'
        )

        _cmd(
            [
                'sudo',
                'sh', '-c', cp_wellknown_sh,
            ],
        )

        # check that the file is in place

        if not disable_check:
            wellknown_url = 'http://{0}{1}/.well-known/acme-challenge/{2}'.format(
                domain,
                '' if check_port is None else f':{check_port}',
                token,
            )

            if not _do_request(wellknown_url)[0] == key_authorization:
                raise ValueError(
                    f"Wrote file to {wellknown_path}, but couldn't download {wellknown_url}: "
                    f"wrong content!",
                )

        # say the challenge is done

        ssr().send_signed_request(
            challenge['url'],
            {},
            err_msg=f'Error submitting challenges: {domain}',
        )

        authorization = ssr().poll_until_not(
            auth_url,
            ['pending'],
            err_msg=f'Error checking challenge status for {domain}',
        )

        if authorization['status'] != 'valid':
            raise ValueError(f'Challenge did not pass for {domain}: {authorization}')

        rm_wellknown_sh = f'rm {shlex.quote(wellknown_path)}'

        _cmd(
            [
                'sudo'
                'sh', '-c', rm_wellknown_sh,
            ],
        )

        log.info(f'{domain} verified!')

    # finalize the order with the csr

    log.info('Signing certificate...')

    csr_der = check.not_none(_cmd(
        [
            'openssl',
            'req',
            '-in', csr,
            '-outform', 'DER',
        ],
        err_msg='DER Export Error',
    ))

    ssr().send_signed_request(
        order['finalize'],
        {
            'csr': _b64_encode(csr_der),
        },
        err_msg='Error finalizing order',
    )

    # poll the order to monitor when it's done

    order = ssr().poll_until_not(
        order_headers['Location'],
        ['pending', 'processing'],
        err_msg='Error checking order status',
    )

    if order['status'] != 'valid':
        raise ValueError(f'Order failed: {order}')

    # download the certificate

    certificate_pem = ssr().send_signed_request(
        order['certificate'],
        None,
        err_msg='Certificate download failed',
    ).data

    log.info('Certificate signed!')

    return certificate_pem


def main(argv: ta.Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            This script automates the process of getting a signed TLS certificate from Let's Encrypt using the ACME
            protocol.

            It will need to be run on your server and have access to your private account key, so PLEASE READ THROUGH
            IT!

            It's only ~200 lines, so it won't take long.

            Example Usage:

                python acme_tiny.py \\
                    --account-key ./account.key \\
                    --csr ./domain.csr \\
                    --acme-dir /usr/share/nginx/html/.well-known/acme-challenge/ \\
                    > signed_chain.crt

            Example ZeroSSL Usage:

                python acme_tiny.py \
                    --account-key /etc/ssl/acme/account.key \\
                    --csr /etc/ssl/acme/yourdomain.csr \\
                    --acme-dir /var/www/.well-known/acme-challenge \\
                    --directory-url https://acme.zerossl.com/v2/DV90 \\
                    --eab-kid 'YOUR_EAB_KID' \\
                    --eab-hmac-key 'YOUR_EAB_HMAC_KEY' \\
                    > /etc/ssl/acme/yourdomain.crt

            """),
    )

    parser.add_argument(
        '--account-key',
        required=True,
        help="path to your Let's Encrypt account private key",
    )

    parser.add_argument(
        '--csr',
        required=True,
        help='path to your certificate signing request',
    )

    parser.add_argument(
        '--acme-dir',
        required=True,
        help='path to the .well-known/acme-challenge/ directory',
    )

    parser.add_argument(
        '--quiet',
        action='store_const',
        const=logging.ERROR,
        help='suppress output except for errors',
    )

    parser.add_argument(
        '--disable-check',
        default=False,
        action='store_true',
        help='disable checking if the challenge file is hosted correctly before telling the CA',
    )

    parser.add_argument(
        '--directory-url',
        default=DEFAULT_DIRECTORY_URL,
        help="certificate authority directory url, default is Let's Encrypt",
    )

    parser.add_argument(
        '--contact',
        metavar='CONTACT',
        default=None,
        nargs='*',
        help='Contact details (e.g. mailto:aaa@bbb.com) for your account-key',
    )

    parser.add_argument(
        '--check-port',
        metavar='PORT',
        default=None,
        help='what port to use when self-checking the challenge file, default is port 80',
    )

    parser.add_argument(
        '--eab-kid',
        metavar='EAB_KID',
        default=None,
        help='External Account Binding key ID (e.g. from ZeroSSL)',
    )

    parser.add_argument(
        '--eab-hmac-key',
        metavar='EAB_HMAC_KEY',
        default=None,
        help='External Account Binding HMAC key (base64url, from ZeroSSL)',
    )

    args = parser.parse_args(argv)

    log.setLevel(args.quiet or logging.INFO)
    log.addHandler(logging.StreamHandler())

    signed_crt = get_crt(
        args.account_key,
        args.csr,
        args.acme_dir,
        disable_check=args.disable_check,
        directory_url=args.directory_url,
        contact=args.contact,
        check_port=args.check_port,
        eab_kid=args.eab_kid,
        eab_hmac_key=args.eab_hmac_key,
    )

    sys.stdout.write(signed_crt)


if __name__ == '__main__': # pragma: no cover
    main(sys.argv[1:])
