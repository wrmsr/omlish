# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
# MIT License
#
# Copyright (c) 2012 Daniel Holth <dholth@fastmail.fm> and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/pypa/wheel/blob/7bb46d7727e6e89fe56b3c78297b3af2672bbbe2/src/wheel/wheelfile.py
import base64
import csv
import hashlib
import io
import os.path
import re
import stat
import time
import typing as ta
import zipfile


##


class WheelError(Exception):
    pass


# Non-greedy matching of an optional build number may be too clever (more invalid wheel filenames will match). Separate
# regex for .dist-info?
WHEEL_INFO_RE = re.compile(
    r'^'
    r'(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]+?))'
    r'(-(?P<build>\d[^\s-]*))?-'
    r'(?P<pyver>[^\s-]+?)-'
    r'(?P<abi>[^\s-]+?)-'
    r'(?P<plat>\S+)'
    r'\.whl$',
    re.VERBOSE,
)


class WheelFile(zipfile.ZipFile):
    """
    A ZipFile derivative class that also reads SHA-256 hashes from .dist-info/RECORD and checks any read files against
    those.
    """

    _default_algorithm = hashlib.sha256

    def __init__(
            self,
            file: str,
            mode: str = 'r',  # ta.Literal["r", "w", "x", "a"]
            compression: int = zipfile.ZIP_DEFLATED,
    ) -> None:
        basename = os.path.basename(file)
        self.parsed_filename = WHEEL_INFO_RE.match(basename)
        if not basename.endswith('.whl') or self.parsed_filename is None:
            raise WheelError(f'Bad wheel filename {basename!r}')

        super().__init__(  # type: ignore
            file,
            mode,
            compression=compression,
            allowZip64=True,
        )

        self.dist_info_path = '{}.dist-info'.format(self.parsed_filename.group('namever'))
        self.record_path = self.dist_info_path + '/RECORD'
        self._file_hashes: ta.Dict[str, ta.Union[ta.Tuple[None, None], ta.Tuple[int, bytes]]] = {}
        self._file_sizes: ta.Dict[str, int] = {}

        if mode == 'r':
            # Ignore RECORD and any embedded wheel signatures
            self._file_hashes[self.record_path] = None, None
            self._file_hashes[self.record_path + '.jws'] = None, None
            self._file_hashes[self.record_path + '.p7s'] = None, None

            # Fill in the expected hashes by reading them from RECORD
            try:
                record = self.open(self.record_path)
            except KeyError:
                raise WheelError(f'Missing {self.record_path} file') from None

            with record:
                for line in csv.reader(io.TextIOWrapper(record, newline='', encoding='utf-8')):
                    path, hash_sum, size = line
                    if not hash_sum:
                        continue

                    algorithm, hash_sum = hash_sum.split('=')
                    try:
                        hashlib.new(algorithm)
                    except ValueError:
                        raise WheelError(f'Unsupported hash algorithm: {algorithm}') from None

                    if algorithm.lower() in {'md5', 'sha1'}:
                        raise WheelError(f'Weak hash algorithm ({algorithm}) is not permitted by PEP 427')

                    self._file_hashes[path] = (  # type: ignore
                        algorithm,
                        self._urlsafe_b64decode(hash_sum.encode('ascii')),
                    )

    @staticmethod
    def _urlsafe_b64encode(data: bytes) -> bytes:
        """urlsafe_b64encode without padding"""
        return base64.urlsafe_b64encode(data).rstrip(b'=')

    @staticmethod
    def _urlsafe_b64decode(data: bytes) -> bytes:
        """urlsafe_b64decode without padding"""
        pad = b'=' * (4 - (len(data) & 3))
        return base64.urlsafe_b64decode(data + pad)

    def open(  # type: ignore  # noqa
            self,
            name_or_info: ta.Union[str, zipfile.ZipInfo],
            mode: str = 'r',  # ta.Literal["r", "w"]
            pwd: ta.Optional[bytes] = None,
    ) -> ta.IO[bytes]:
        def _update_crc(newdata: bytes) -> None:
            eof = ef._eof  # type: ignore  # noqa
            update_crc_orig(newdata)
            running_hash.update(newdata)
            if eof and running_hash.digest() != expected_hash:
                raise WheelError(f"Hash mismatch for file '{ef_name}'")

        ef_name = name_or_info.filename if isinstance(name_or_info, zipfile.ZipInfo) else name_or_info
        if (
                mode == 'r'
                and not ef_name.endswith('/')
                and ef_name not in self._file_hashes
        ):
            raise WheelError(f"No hash found for file '{ef_name}'")

        ef = super().open(name_or_info, mode, pwd)  # noqa
        if mode == 'r' and not ef_name.endswith('/'):
            algorithm, expected_hash = self._file_hashes[ef_name]
            if expected_hash is not None:
                # Monkey patch the _update_crc method to also check for the hash from RECORD
                running_hash = hashlib.new(algorithm)  # type: ignore
                update_crc_orig, ef._update_crc = ef._update_crc, _update_crc  # type: ignore  # noqa

        return ef

    def write_files(self, base_dir: str) -> None:
        deferred: list[tuple[str, str]] = []
        for root, dirnames, filenames in os.walk(base_dir):
            # Sort the directory names so that `os.walk` will walk them in a defined order on the next iteration.
            dirnames.sort()
            for name in sorted(filenames):
                path = os.path.normpath(os.path.join(root, name))
                if os.path.isfile(path):
                    arcname = os.path.relpath(path, base_dir).replace(os.path.sep, '/')
                    if arcname == self.record_path:
                        pass
                    elif root.endswith('.dist-info'):
                        deferred.append((path, arcname))
                    else:
                        self.write(path, arcname)

        deferred.sort()
        for path, arcname in deferred:
            self.write(path, arcname)

    def write(  # type: ignore  # noqa
            self,
            filename: str,
            arcname: ta.Optional[str] = None,
            compress_type: ta.Optional[int] = None,
    ) -> None:
        with open(filename, 'rb') as f:
            st = os.fstat(f.fileno())
            data = f.read()

        zinfo = zipfile.ZipInfo(
            arcname or filename,
            date_time=self._get_zipinfo_datetime(st.st_mtime),
        )
        zinfo.external_attr = (stat.S_IMODE(st.st_mode) | stat.S_IFMT(st.st_mode)) << 16
        zinfo.compress_type = compress_type or self.compression
        self.writestr(zinfo, data, compress_type)

    _MINIMUM_TIMESTAMP = 315532800  # 1980-01-01 00:00:00 UTC

    @classmethod
    def _get_zipinfo_datetime(cls, timestamp: ta.Optional[float] = None) -> ta.Any:
        # Some applications need reproducible .whl files, but they can't do this without forcing the timestamp of the
        # individual ZipInfo objects. See issue #143.
        timestamp = int(os.environ.get('SOURCE_DATE_EPOCH', timestamp or time.time()))
        timestamp = max(timestamp, cls._MINIMUM_TIMESTAMP)
        return time.gmtime(timestamp)[0:6]

    def writestr(  # type: ignore  # noqa
            self,
            zinfo_or_arcname: ta.Union[str, zipfile.ZipInfo],
            data: ta.Any,  # SizedBuffer | str,
            compress_type: ta.Optional[int] = None,
    ) -> None:
        if isinstance(zinfo_or_arcname, str):
            zinfo_or_arcname = zipfile.ZipInfo(
                zinfo_or_arcname,
                date_time=self._get_zipinfo_datetime(),
            )
            zinfo_or_arcname.compress_type = self.compression
            zinfo_or_arcname.external_attr = (0o664 | stat.S_IFREG) << 16

        if isinstance(data, str):
            data = data.encode('utf-8')

        super().writestr(zinfo_or_arcname, data, compress_type)
        fname = (
            zinfo_or_arcname.filename
            if isinstance(zinfo_or_arcname, zipfile.ZipInfo)
            else zinfo_or_arcname
        )
        if fname != self.record_path:
            hash_ = self._default_algorithm(data)  # type: ignore
            self._file_hashes[fname] = (  # type: ignore
                hash_.name,
                self._urlsafe_b64encode(hash_.digest()).decode('ascii'),
            )
            self._file_sizes[fname] = len(data)

    def close(self) -> None:
        # Write RECORD
        if self.fp is not None and self.mode == 'w' and self._file_hashes:
            data = io.StringIO()
            writer = csv.writer(data, delimiter=',', quotechar='"', lineterminator='\n')
            writer.writerows((
                (fname, algorithm + '=' + hash_, self._file_sizes[fname])  # type: ignore
                for fname, (algorithm, hash_) in self._file_hashes.items()
            ))
            writer.writerow((format(self.record_path), '', ''))
            self.writestr(self.record_path, data.getvalue())

        super().close()
