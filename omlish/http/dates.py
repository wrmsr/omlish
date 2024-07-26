# Copyright 2007 Pallets
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#     disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3.  Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import datetime
import email.utils
import time

from .. import check


def _dt_as_utc(dt: datetime.datetime | None) -> datetime.datetime | None:
    if dt is None:
        return dt

    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    elif dt.tzinfo != datetime.UTC:
        return dt.astimezone(datetime.UTC)

    return dt


def http_date(timestamp: datetime.datetime | datetime.date | float | time.struct_time | None = None) -> str:
    if isinstance(timestamp, datetime.date):
        if not isinstance(timestamp, datetime.datetime):
            # Assume plain date is midnight UTC.
            timestamp = datetime.datetime.combine(timestamp, datetime.time(), tzinfo=datetime.UTC)
        else:
            # Ensure datetime is timezone-aware.
            timestamp = _dt_as_utc(timestamp)

        return email.utils.format_datetime(check.not_none(timestamp), usegmt=True)

    if isinstance(timestamp, time.struct_time):
        timestamp = time.mktime(timestamp)

    return email.utils.formatdate(timestamp, usegmt=True)


def parse_date(value: str | None) -> datetime.datetime | None:
    if value is None:
        return None

    try:
        dt = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)

    return dt
