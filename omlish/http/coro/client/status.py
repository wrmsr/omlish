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
import typing as ta

from ....lite.check import check
from ..io import CoroHttpIo
from .errors import CoroHttpClientErrors


#


class CoroHttpClientStatusLine(ta.NamedTuple):
    version: str
    status: int
    reason: str

    @classmethod
    def read(cls) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], 'CoroHttpClientStatusLine']:
        line = str(check.isinstance((yield CoroHttpIo.ReadLineIo(CoroHttpIo.MAX_LINE + 1)), bytes), 'iso-8859-1')
        if len(line) > CoroHttpIo.MAX_LINE:
            raise CoroHttpClientErrors.LineTooLongError(CoroHttpClientErrors.LineTooLongError.LineType.STATUS)
        if not line:
            # Presumably, the server closed the connection before sending a valid response.
            raise CoroHttpClientErrors.RemoteDisconnectedError('Remote end closed connection without response')

        version = ''
        reason = ''
        status_str = ''
        try:
            version, status_str, reason = line.split(None, 2)
        except ValueError:
            try:
                version, status_str = line.split(None, 1)
            except ValueError:
                # empty version will cause next test to fail.
                pass

        if not version.startswith('HTTP/'):
            raise CoroHttpClientErrors.BadStatusLineError(line)

        # The status code is a three-digit number
        try:
            status = int(status_str)
        except ValueError:
            raise CoroHttpClientErrors.BadStatusLineError(line) from None

        if status < 100 or status > 999:
            raise CoroHttpClientErrors.BadStatusLineError(line)

        return cls(version, status, reason)
