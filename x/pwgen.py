"""
TODO:
 - len
 - required character classes
  - lowercase
  - uppercase
  - digits
  - symbols
 - move to omlish/secrets
 - argparse, CliCmd
"""
import secrets
import string


class PasswordGenerator:
    def __init__(self,
                 length: int = 12,
                 required_chars: str = "",
                 permitted_chars: str = string.ascii_letters + string.digits + string.punctuation):
        """
        Initialize the password generator.

        :param length: The desired length of the password (default is 12).
        :param required_chars: Characters that must be present in the password (default is none).
        :param permitted_chars: Characters that can be used in the password (default is all letters, digits, punctuation).
        """
        self.length = length
        self.required_chars = required_chars
        self.permitted_chars = permitted_chars

    def generate(self) -> str:
        """
        Generate a secure password based on the specified requirements.

        :return: A generated password as a string.
        """
        if len(self.required_chars) > self.length:
            raise ValueError("Number of required characters exceeds password length.")

        # Ensure all required characters are in the password
        password_chars = list(self.required_chars)

        # Calculate remaining length needed
        remaining_length = self.length - len(password_chars)

        # Add random permitted characters until the password reaches the desired length
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(self.permitted_chars))

        # Shuffle the characters to ensure randomness
        secrets.SystemRandom().shuffle(password_chars)

        return ''.join(password_chars)
