"""
https://docs.python.org/3/library/bz2.html#bz2.BZ2Compressor
https://docs.python.org/3/library/zlib.html#zlib.decompressobj
"""
import abc
import typing as ta


class Decompressor(abc.ABC):
    @property
    @abc.abstractmethod
    def unused_data(self) -> bytes:
        """
        A bytes object which contains any bytes past the end of the compressed data. That is, this remains b"" until the
        last byte that contains compression data is available. If the whole bytestring turned out to contain compressed
        data, this is b"", an empty bytes object.
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unconsumed_tail(self) -> bytes:
        """
        A bytes object that contains any data that was not consumed by the last decompress() call because it exceeded
        the limit for the uncompressed data buffer. This data has not yet been seen by the zlib machinery, so you must
        feed it (possibly with further data concatenated to it) back to a subsequent decompress() method call in order
        to get correct output.
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def eof(self) -> bool:
        """
        A boolean indicating whether the end of the compressed data stream has been reached.

        This makes it possible to distinguish between a properly formed compressed stream, and an incomplete or
        truncated one.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def decompress(self, data: bytes, max_length: int = 0) -> bytes:
        """
        Decompress data, returning a bytes object containing the uncompressed data corresponding to at least part of the
        data in string. This data should be concatenated to the output produced by any preceding calls to the
        decompress() method. Some of the input data may be preserved in internal buffers for later processing.

        If the optional parameter max_length is non-zero then the return value will be no longer than max_length. This
        may mean that not all of the compressed input can be processed; and unconsumed data will be stored in the
        attribute unconsumed_tail. This bytestring must be passed to a subsequent call to decompress() if decompression
        is to continue. If max_length is zero then the whole input is decompressed, and unconsumed_tail is empty.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def flush(self, *length: int) -> None:
        """
        All pending input is processed, and a bytes object containing the remaining uncompressed output is returned.
        After calling flush(), the decompress() method cannot be called again; the only realistic action is to delete
        the object.

        The optional parameter length sets the initial size of the output buffer.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def copy(self) -> ta.Self:
        """
        Returns a copy of the decompression object. This can be used to save the state of the decompressor midway
        through the data stream in order to speed up random seeks into the stream at a future point.
        """

        raise NotImplementedError


class Compressor(abc.ABC):
    @abc.abstractmethod
    def compress(self, data: bytes) -> bytes:
        """
        Compress data, returning a bytes object containing compressed data for at least part of the data in data. This
        data should be concatenated to the output produced by any preceding calls to the compress() method. Some input
        may be kept in internal buffers for later processing.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def flush(self, *mode: int) -> bytes:
        """
        All pending input is processed, and a bytes object containing the remaining compressed output is returned. mode
        can be selected from the constants Z_NO_FLUSH, Z_PARTIAL_FLUSH, Z_SYNC_FLUSH, Z_FULL_FLUSH, Z_BLOCK
        (zlib 1.2.3.4), or Z_FINISH, defaulting to Z_FINISH. Except Z_FINISH, all constants allow compressing further
        bytestrings of data, while Z_FINISH finishes the compressed stream and prevents compressing any more data. After
        calling flush() with mode set to Z_FINISH, the compress() method cannot be called again; the only realistic
        action is to delete the object.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def copy(self) -> ta.Self:
        """
        Returns a copy of the compression object. This can be used to efficiently compress a set of data that share a
        common initial prefix.
        """

        raise NotImplementedError
