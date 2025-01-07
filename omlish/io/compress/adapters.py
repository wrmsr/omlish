# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
# ~> https://github.com/python/cpython/blob/f19c50a4817ffebb26132182ed8cec6a72342cc0/Lib/_compression.py
import typing as ta

from ... import check
from ..coro import BytesSteppedCoro
from ..coro import BytesSteppedReaderCoro
from .abc import CompressorObject
from .abc import NeedsInputDecompressorObject
from .abc import UnconsumedTailDecompressorObject


##


class CompressorObjectIncrementalAdapter:
    def __init__(
            self,
            factory: ta.Callable[..., CompressorObject],
    ) -> None:
        super().__init__()

        self._factory = factory

    def __call__(self) -> BytesSteppedCoro:
        compressor = self._factory()

        while True:
            data = check.isinstance((yield None), bytes)
            if not data:
                break

            compressed = compressor.compress(data)
            if compressed:
                check.none((yield compressed))

        if (fl := compressor.flush()):
            check.none((yield fl))

        check.none((yield b''))


##


class DecompressorObjectIncrementalAdapter:
    def __init__(
            self,
            factory: ta.Callable[..., NeedsInputDecompressorObject | UnconsumedTailDecompressorObject],
            *,
            trailing_error: type[BaseException] | tuple[type[BaseException], ...] = (),
    ) -> None:
        super().__init__()

        self._factory = factory
        self._trailing_error = trailing_error

    def __call__(self) -> BytesSteppedReaderCoro:
        pos = 0

        data = None  # Default if EOF is encountered

        decompressor = self._factory()

        while True:
            # Depending on the input data, our call to the decompressor may not return any data. In this case, try again
            # after reading another block.
            while True:
                if decompressor.eof:
                    rawblock = decompressor.unused_data
                    if not rawblock:
                        rawblock = check.isinstance((yield None), bytes)
                    if not rawblock:
                        break

                    # Continue to next stream.
                    decompressor = self._factory()

                    try:
                        data = decompressor.decompress(rawblock)
                    except self._trailing_error:
                        # Trailing data isn't a valid compressed stream; ignore it.
                        break

                else:
                    if hasattr(decompressor, 'needs_input'):
                        if decompressor.needs_input:
                            rawblock = check.isinstance((yield None), bytes)
                            if not rawblock:
                                raise EOFError('Compressed file ended before the end-of-stream marker was reached')
                        else:
                            rawblock = b''

                    elif hasattr(decompressor, 'unconsumed_tail'):
                        if not (rawblock := decompressor.unconsumed_tail):
                            rawblock = check.isinstance((yield None), bytes)
                            if not rawblock:
                                raise EOFError('Compressed file ended before the end-of-stream marker was reached')

                    else:
                        raise TypeError(decompressor)

                    data = decompressor.decompress(rawblock)

                if data:
                    break

            if not data:
                check.none((yield b''))
                return

            pos += len(data)
            check.none((yield data))
            data = None
