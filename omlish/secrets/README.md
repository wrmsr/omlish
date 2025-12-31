# Overview

Security and cryptography utilities including password hashing, SSL/TLS helpers, OpenSSL integration, and secure random
generation. Provides high-level APIs for common cryptographic operations.

# Key Features

- **Password hashing** - Secure password hashing with bcrypt/argon2/scrypt.
- **SSL/TLS** - SSL context creation, certificate handling, temporary certificate generation.
- **OpenSSL integration** - Wrappers around OpenSSL command-line tools.
- **Subprocess helpers** - Secure subprocess execution for cryptographic tools.
- **Marshaling** - Secure marshaling of sensitive data.
- **Random generation** - Cryptographically secure random data generation.

# Notable Modules

- **[pwhash](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/pwhash.py)** - Password hashing with
  bcrypt/argon2/scrypt support.
- **[ssl](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/ssl.py)** - SSL context creation and certificate
  handling.
- **[tempssl](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/tempssl.py)** - Temporary self-signed
  certificate generation for testing.
- **[openssl](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/openssl.py)** - OpenSSL command-line wrapper
  utilities.
- **[crypto](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/crypto.py)** - General cryptographic utilities.
- **[secrets](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/secrets.py)** - Secure random generation.
- **[marshal](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/marshal.py)** - Marshaling of sensitive data.
- **[subprocesses](https://github.com/wrmsr/omlish/blob/master/omlish/secrets/subprocesses.py)** - Secure subprocess
  execution.

# Example Usage

```python
from omlish.secrets import pwhash

# Hash a password
hashed = pwhash.hash_password('my_password', algorithm='bcrypt')

# Verify a password
if pwhash.verify_password('my_password', hashed):
    print("Password correct!")

# Generate temporary SSL certificate for testing
from omlish.secrets import tempssl
cert, key = tempssl.generate_temp_certificate()
```

# Design Philosophy

Security utilities should:
- **Use proven algorithms** - Rely on well-tested cryptographic libraries, not custom crypto.
- **Provide safe defaults** - Make secure choices easy and insecure choices hard.
- **Be explicit** - Don't hide security-critical operations behind magic.
- **Support testing** - Provide utilities like temp certificates for development/testing.

This package wraps existing cryptographic libraries (like `cryptography`, `bcrypt`) with higher-level APIs while
maintaining security best practices.
