import abc

from omlish import lang


class FileTransfer(lang.Abstract):
    @abc.abstractmethod
    async def get_files(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def put_files(self) -> None:
        raise NotImplementedError


class LocalFileTransfer(FileTransfer):
    @abc.abstractmethod
    async def get_files(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def put_files(self) -> None:
        raise NotImplementedError
