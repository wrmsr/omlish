# @omlish-lite
# Copyright (c) Donald Stufft and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#        following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#        following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. This file is dual licensed under the terms of the
# Apache License, Version 2.0, and the BSD License. See the LICENSE file in the root of this repository for complete
# details.
# https://github.com/pypa/packaging/blob/cf2cbe2aec28f87c6228a6fb136c27931c9af407/src/packaging/utils.py
import re


##


# Core metadata spec for `Name`
_CANONICAL_NAME_VALIDATE_PATTERN = re.compile(r'^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$', re.IGNORECASE)
_CANONICAL_NAME_CANONICALIZE_PATTERN = re.compile(r'[-_.]+')
_CANONICAL_NAME_NORMALIZED_PATTERN = re.compile(r'^([a-z0-9]|[a-z0-9]([a-z0-9-](?!--))*[a-z0-9])$')

# PEP 427: The build number must start with a digit.
_CANONICAL_NAME_BUILD_TAG_PATTERN = re.compile(r'(\d+)(.*)')


def canonicalize_name(name: str, *, validate: bool = False) -> str:
    if validate and not _CANONICAL_NAME_VALIDATE_PATTERN.match(name):
        raise NameError(f'name is invalid: {name!r}')
    # This is taken from PEP 503.
    value = _CANONICAL_NAME_CANONICALIZE_PATTERN.sub('-', name).lower()
    return value


def is_normalized_name(name: str) -> bool:
    return _CANONICAL_NAME_NORMALIZED_PATTERN.match(name) is not None
