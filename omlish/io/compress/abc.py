"""
https://docs.python.org/3/library/bz2.html#bz2.BZ2Compressor
https://docs.python.org/3/library/zlib.html#zlib.decompressobj
https://docs.python.org/3/library/lzma.html#lzma.LZMADecompressor
"""
import abc


##


class CompressorObject(abc.ABC):
    @abc.abstractmethod
    def compress(self, data: bytes) -> bytes:
        """
        Provide data to the compressor object. Returns a chunk of compressed data if possible, or an empty byte string
        otherwise.

        When you have finished providing data to the compressor, call the flush() method to finish the compression
        process.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def flush(self) -> bytes:
        """
        Finish the compression process. Returns the compressed data left in internal buffers.

        The compressor object may not be used after this method has been called.
        """

        raise NotImplementedError


##


class DecompressorObject(abc.ABC):
    @property
    @abc.abstractmethod
    def unused_data(self) -> bytes:
        """
        Data found after the end of the compressed stream.

        If this attribute is accessed before the end of the stream has been reached, its value will be b''.
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def eof(self) -> bool:
        """True if the end-of-stream marker has been reached."""

        raise NotImplementedError

    @abc.abstractmethod
    def decompress(self, data: bytes, *max_length: int) -> bytes:
        """
        Decompress data, returning a bytes object containing the uncompressed data corresponding to at least part of the
        data in string. This data should be concatenated to the output produced by any preceding calls to the
        decompress() method. Some of the input data may be preserved in internal buffers for later processing.

        If the optional parameter max_length is non-zero then the return value will be no longer than max_length.
        """

        raise NotImplementedError


class NeedsInputDecompressorObject(DecompressorObject):
    """
    Used by:
     - bz2.BZ2Decompressor
     - lzma.LZMADecompressor
    """

    @property
    @abc.abstractmethod
    def needs_input(self) -> bool:
        """
        False if the decompress() method can provide more decompressed data before requiring new uncompressed input.
        """

        raise NotImplementedError


class UnconsumedTailDecompressorObject(DecompressorObject):
    """
    Used by:
     - zlib.decompressobj
    """

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
