# @omlish-lite
# ruff: noqa: UP006 UP007 UP043 UP045
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
import email.message
import email.parser
import typing as ta

from ....lite.check import check
from ..io import CoroHttpIo
from .errors import CoroHttpClientErrors


##


class CoroHttpClientHeaders:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    MAX_HEADERS: ta.ClassVar[int] = 100

    @classmethod
    def read_headers(cls) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], ta.List[bytes]]:
        """
        Reads potential header lines into a list from a file pointer.

        Length of line is limited by MAX_LINE, and number of headers is limited by MAX_HEADERS.
        """

        headers = []
        while True:
            line = check.isinstance((yield CoroHttpIo.ReadLineIo(CoroHttpIo.MAX_LINE + 1)), bytes)
            if len(line) > CoroHttpIo.MAX_LINE:
                raise CoroHttpClientErrors.LineTooLongError(CoroHttpClientErrors.LineTooLongError.LineType.HEADER)

            headers.append(line)
            if len(headers) > cls.MAX_HEADERS:
                raise CoroHttpClientErrors.ClientError(f'got more than {cls.MAX_HEADERS} headers')

            if line in (b'\r\n', b'\n', b''):
                break

        return headers

    @classmethod
    def parse_header_lines(cls, header_lines: ta.Sequence[bytes]) -> email.message.Message:
        """
        Parses only RFC2822 headers from header lines.

        email Parser wants to see strings rather than bytes. But a TextIOWrapper around self.rfile would buffer too many
        bytes from the stream, bytes which we later need to read as bytes. So we read the correct bytes here, as bytes,
        for email Parser to parse.
        """

        text = b''.join(header_lines).decode('iso-8859-1')
        return email.parser.Parser().parsestr(text)

    @classmethod
    def parse_headers(cls) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], email.message.Message]:
        """Parses only RFC2822 headers from a file pointer."""

        headers = yield from cls.read_headers()
        return cls.parse_header_lines(headers)
