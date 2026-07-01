import base64
import hashlib
import json
import os
import typing as ta

import cryptography.exceptions as cry_exc
import cryptography.hazmat.primitives.asymmetric.x25519 as cry_x25519
import cryptography.hazmat.primitives.ciphers.aead as cry_aead
import cryptography.hazmat.primitives.hashes as cry_hph
import cryptography.hazmat.primitives.kdf.hkdf as cry_hkdf
import cryptography.hazmat.primitives.serialization as cry_hps


##


SUITE = 'miniage1:x25519-hkdf-sha256-chacha20poly1305-wrap+aes-256-gcm'
CONTEXT = b'com.yourname.secretbox.v1'


def b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')


def b64d(text: str) -> bytes:
    pad = '=' * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def canonical_json(obj: ta.Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True,
    ).encode('utf-8')


def raw_private_key(priv: cry_x25519.X25519PrivateKey) -> bytes:
    return priv.private_bytes(
        encoding=cry_hps.Encoding.Raw,
        format=cry_hps.PrivateFormat.Raw,
        encryption_algorithm=cry_hps.NoEncryption(),
    )


def raw_public_key(pub: cry_x25519.X25519PublicKey) -> bytes:
    return pub.public_bytes(
        encoding=cry_hps.Encoding.Raw,
        format=cry_hps.PublicFormat.Raw,
    )


def generate_identity() -> tuple[str, str]:
    """
    Returns:
      private_identity, public_recipient

    Store private_identity only on the device.
    Commit/share public_recipient freely.
    """

    priv = cry_x25519.X25519PrivateKey.generate()
    priv_raw = raw_private_key(priv)
    pub_raw = raw_public_key(priv.public_key())
    return 'MSK1.' + b64e(priv_raw), 'MPK1.' + b64e(pub_raw)


def load_private(identity: str) -> cry_x25519.X25519PrivateKey:
    if not identity.startswith('MSK1.'):
        raise ValueError('private identity must start with MSK1.')
    raw = b64d(identity[5:])
    if len(raw) != 32:
        raise ValueError('bad X25519 private key length')
    return cry_x25519.X25519PrivateKey.from_private_bytes(raw)


def load_public(recipient: str) -> tuple[cry_x25519.X25519PublicKey, bytes]:
    if not recipient.startswith('MPK1.'):
        raise ValueError('recipient must start with MPK1.')
    raw = b64d(recipient[5:])
    if len(raw) != 32:
        raise ValueError('bad X25519 public key length')
    return cry_x25519.X25519PublicKey.from_public_bytes(raw), raw


def recipient_kid(pub_raw: bytes) -> str:
    # Not secret. Only for fast recipient matching / display.
    return b64e(hashlib.sha256(pub_raw).digest()[:12])


def derive_wrap_key(shared_secret: bytes, epk_raw: bytes, recipient_pub_raw: bytes) -> bytes:
    if shared_secret == b'\x00' * 32:
        raise ValueError('invalid all-zero X25519 shared secret')

    return cry_hkdf.HKDF(
        algorithm=cry_hph.SHA256(),
        length=32,
        salt=epk_raw + recipient_pub_raw,
        info=CONTEXT + b'/x25519-wrap',
    ).derive(shared_secret)


def wrap_aad(kid: str, epk_raw: bytes) -> bytes:
    return CONTEXT + b'/wrap-aad\x00' + kid.encode('ascii') + b'\x00' + epk_raw


def encrypt_bytes(plaintext: bytes, recipients: list[str]) -> bytes:
    if not recipients:
        raise ValueError('need at least one recipient')

    data_key = cry_aead.AESGCM.generate_key(bit_length=256)
    recipient_entries: list[dict[str, str]] = []

    for recipient in recipients:
        recipient_pub, recipient_pub_raw = load_public(recipient)
        kid = recipient_kid(recipient_pub_raw)

        eph_priv = cry_x25519.X25519PrivateKey.generate()
        eph_pub_raw = raw_public_key(eph_priv.public_key())

        shared = eph_priv.exchange(recipient_pub)
        wrap_key = derive_wrap_key(shared, eph_pub_raw, recipient_pub_raw)

        wrap_nonce = os.urandom(12)
        wrapped_key = cry_aead.ChaCha20Poly1305(wrap_key).encrypt(
            wrap_nonce,
            data_key,
            wrap_aad(kid, eph_pub_raw),
        )

        recipient_entries.append(
            {
                'type': 'x25519',
                'kid': kid,
                'epk': b64e(eph_pub_raw),
                'nonce': b64e(wrap_nonce),
                'wrap': b64e(wrapped_key),
            },
        )

    header = {
        'v': 1,
        'suite': SUITE,
        'recipients': recipient_entries,
    }

    payload_nonce = os.urandom(12)
    payload_ct = cry_aead.AESGCM(data_key).encrypt(
        payload_nonce,
        plaintext,
        canonical_json(header),
    )

    doc = {
        **header,
        'payload': {
            'nonce': b64e(payload_nonce),
            'ct': b64e(payload_ct),
        },
    }

    return json.dumps(doc, indent=2, sort_keys=True).encode('utf-8') + b'\n'


def decrypt_bytes(blob: bytes, identity: str) -> bytes:
    doc = json.loads(blob)

    if doc.get('v') != 1:
        raise ValueError('unsupported version')
    if doc.get('suite') != SUITE:
        raise ValueError('unsupported crypto suite')

    priv = load_private(identity)
    own_pub_raw = raw_public_key(priv.public_key())
    own_kid = recipient_kid(own_pub_raw)

    data_key: bytes | None = None

    for entry in doc.get('recipients', []):
        if entry.get('type') != 'x25519':
            continue

        # Optimization only. You can remove this check and just try all stanzas.
        if entry.get('kid') != own_kid:
            continue

        try:
            epk_raw = b64d(entry['epk'])
            if len(epk_raw) != 32:
                continue

            epk = cry_x25519.X25519PublicKey.from_public_bytes(epk_raw)
            shared = priv.exchange(epk)
            wrap_key = derive_wrap_key(shared, epk_raw, own_pub_raw)

            candidate = cry_aead.ChaCha20Poly1305(wrap_key).decrypt(
                b64d(entry['nonce']),
                b64d(entry['wrap']),
                wrap_aad(entry['kid'], epk_raw),
            )

        except (cry_exc.InvalidTag, ValueError, KeyError):
            continue

        if len(candidate) != 32:
            continue

        data_key = candidate
        break

    if data_key is None:
        raise ValueError('file is not encrypted to this identity')

    header = {
        'v': doc['v'],
        'suite': doc['suite'],
        'recipients': doc['recipients'],
    }

    payload = doc['payload']
    return cry_aead.AESGCM(data_key).decrypt(
        b64d(payload['nonce']),
        b64d(payload['ct']),
        canonical_json(header),
    )
