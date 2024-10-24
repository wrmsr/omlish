"""
https://askubuntu.com/questions/11925/a-command-line-clipboard-copy-and-paste-utility
"""
import abc
import subprocess


class Clipboard(abc.ABC):
    @abc.abstractmethod
    def get(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, s: str) -> None:
        raise NotImplementedError


class DarwinClipboard(Clipboard):
    def get(self) -> str:
        return subprocess.check_output(['pbpaste']).decode('utf-8')

    def put(self, s: str) -> None:
        subprocess.run(['pbcopy'], input=s.encode('utf-8'), check=True)
