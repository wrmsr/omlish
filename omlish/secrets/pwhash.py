"""
~> https://github.com/pallets/werkzeug/blob/7a76170c473c26685bdfa2774d083ba2386fc60f/src/werkzeug/security.py
"""
# Copyright 2007 Pallets
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#     disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3.  Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import hashlib
import hmac
import secrets


##


SALT_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
DEFAULT_PBKDF2_ITERATIONS = 600_000


def gen_salt(length: int) -> str:
    if length <= 0:
        raise ValueError('Salt length must be at least 1.')

    return ''.join(secrets.choice(SALT_CHARS) for _ in range(length))


def _hash_internal(
        method: str,
        salt: str,
        password: str,
) -> tuple[str, str]:
    method, *args = method.split(':')
    salt_bytes = salt.encode()
    password_bytes = password.encode()

    if method == 'scrypt':
        if not args:
            n = 2 ** 15
            r = 8
            p = 1
        else:
            try:
                n, r, p = map(int, args)
            except ValueError:
                raise ValueError("'scrypt' takes 3 arguments.") from None

        maxmem = 132 * n * r * p  # ideally 128, but some extra seems needed

        return (
            hashlib.scrypt(
                password_bytes,
                salt=salt_bytes,
                n=n,
                r=r,
                p=p,
                maxmem=maxmem,
            ).hex(),
            f'scrypt:{n}:{r}:{p}',
        )

    elif method == 'pbkdf2':
        len_args = len(args)

        if len_args == 0:
            hash_name = 'sha256'
            iterations = DEFAULT_PBKDF2_ITERATIONS
        elif len_args == 1:
            hash_name = args[0]
            iterations = DEFAULT_PBKDF2_ITERATIONS
        elif len_args == 2:
            hash_name = args[0]
            iterations = int(args[1])
        else:
            raise ValueError("'pbkdf2' takes 2 arguments.")

        return (
            hashlib.pbkdf2_hmac(
                hash_name,
                password_bytes,
                salt_bytes,
                iterations,
            ).hex(),
            f'pbkdf2:{hash_name}:{iterations}',
        )

    else:
        raise ValueError(f"Invalid hash method '{method}'.")


def generate_password_hash(
        password: str,
        method: str = 'scrypt',
        salt_length: int = 16,
) -> str:
    salt = gen_salt(salt_length)
    h, actual_method = _hash_internal(method, salt, password)
    return f'{actual_method}${salt}${h}'


def check_password_hash(pwhash: str, password: str) -> bool:
    try:
        method, salt, hashval = pwhash.split('$', 2)
    except ValueError:
        return False

    return hmac.compare_digest(_hash_internal(method, salt, password)[0], hashval)
