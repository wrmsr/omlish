"""
https://www.tecmint.com/gpg-encrypt-decrypt-files/

gpg --batch --passphrase '' --quick-gen-key wrmsr default default
gpg --batch --passphrase '' --quick-gen-key wrmsr2 default default
echo 'hi there' > secret.txt
gpg -e -u wrmsr -r wrmsr2 secret.txt
gpg -d -o secret2.txt secret.txt.gpg

gpg --batch -c --passphrase-file /var/secret.key -o some.gpg toencrypt.txt

openssl rand -rand /dev/urandom 128 > barf.key
openssl enc -in secret.txt -out secret.txt.enc -e -aes256 -pbkdf2 -kfile barf.key
openssl aes-256-cbc -d -pbkdf2 -in secret.txt.enc -out secret3.txt -kfile barf.key
"""
import abc


class Secrets(abc.ABC):
    @abc.abstractmethod
    def generate_key(self) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def decrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError


class OpensslShellSecrets(Secrets):

    def generate_key(self) -> bytes:
        raise NotImplementedError

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
