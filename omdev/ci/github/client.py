# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import os
import shlex
import typing as ta
import urllib.parse

from omlish.lite.check import check
from omlish.subprocesses import subprocesses

from ..shell import ShellCmd
from ..utils import make_temp_file
from .api import GithubCacheServiceV1
from .curl import GithubServiceCurlClient


##


class GithubCacheClient(abc.ABC):
    class Entry(abc.ABC):  # noqa
        pass

    @abc.abstractmethod
    def get_entry(self, key: str) -> ta.Optional[Entry]:
        raise NotImplementedError

    @abc.abstractmethod
    def download_file(self, entry: Entry, out_file: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, key: str, in_file: str) -> None:
        raise NotImplementedError


##


class GithubCacheServiceV1CurlClient(GithubCacheClient):
    BASE_URL_ENV_KEY = 'ACTIONS_CACHE_URL'
    AUTH_TOKEN_ENV_KEY = 'ACTIONS_RUNTIME_TOKEN'  # noqa

    KEY_SUFFIX_ENV_KEY = 'GITHUB_RUN_ID'

    CACHE_VERSION: ta.ClassVar[int] = 1

    #

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,
            auth_token: ta.Optional[str] = None,

            key_prefix: ta.Optional[str] = None,
            key_suffix: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        #

        if base_url is None:
            base_url = os.environ[self.BASE_URL_ENV_KEY]
        service_url = GithubCacheServiceV1.get_service_url(base_url)

        if auth_token is None:
            auth_token = os.environ.get(self.AUTH_TOKEN_ENV_KEY)

        self._curl = GithubServiceCurlClient(
            service_url,
            auth_token,
            api_version=GithubCacheServiceV1.API_VERSION,
        )

        #

        self._key_prefix = key_prefix

        if key_suffix is None:
            key_suffix = os.environ[self.KEY_SUFFIX_ENV_KEY]
        self._key_suffix = check.non_empty_str(key_suffix)

    #

    KEY_PART_SEPARATOR = '--'

    def fix_key(self, s: str) -> str:
        return self.KEY_PART_SEPARATOR.join([
            *([self._key_prefix] if self._key_prefix else []),
            s,
            self._key_suffix,
        ])

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        artifact: GithubCacheServiceV1.ArtifactCacheEntry

    #

    def build_get_entry_curl_cmd(self, key: str) -> ShellCmd:
        fixed_key = self.fix_key(key)

        qp = dict(
            keys=fixed_key,
            version=str(self.CACHE_VERSION),
        )

        return self._curl.build_cmd(
            'GET',
            shlex.quote('?'.join([
                'cache',
                '&'.join([
                    f'{k}={urllib.parse.quote_plus(v)}'
                    for k, v in qp.items()
                ]),
            ])),
        )

    def get_entry(self, key: str) -> ta.Optional[Entry]:
        fixed_key = self.fix_key(key)
        curl_cmd = self.build_get_entry_curl_cmd(fixed_key)

        obj = self._curl.run_json_cmd(
            curl_cmd,
            success_status_codes=[200, 204],
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    def build_download_get_entry_cmd(self, entry: Entry, out_file: str) -> ShellCmd:
        return ShellCmd(' '.join([
            'aria2c',
            '-x', '4',
            '-o', out_file,
            check.non_empty_str(entry.artifact.archive_location),
        ]))

    def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        dl_cmd = self.build_download_get_entry_cmd(
            check.isinstance(entry, self.Entry),
            out_file,
        )
        dl_cmd.run(subprocesses.check_call)

    #

    def upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))

        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self.CACHE_VERSION),
        )
        reserve_cmd = self._curl.build_post_json_cmd(
            'caches',
            GithubCacheServiceV1.dataclass_to_json(reserve_req),
        )
        reserve_resp_obj: ta.Any = check.not_none(self._curl.run_json_cmd(
            reserve_cmd,
            success_status_codes=[201],
        ))
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            GithubCacheServiceV1.ReserveCacheResponse,
            reserve_resp_obj,
        )
        cache_id = check.isinstance(reserve_resp.cache_id, int)

        #

        tmp_file = make_temp_file()

        print(f'{file_size=}')
        num_written = 0
        chunk_size = 32 * 1024 * 1024
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            ofs = i * chunk_size
            sz = min(chunk_size, file_size - ofs)

            patch_cmd = self._curl.build_cmd(
                'PATCH',
                f'caches/{cache_id}',
                content_type='application/octet-stream',
                headers={
                    'Content-Range': f'bytes {ofs}-{ofs + sz - 1}/*',
                },
            )

            #

            # patch_data_cmd = dc.replace(patch_cmd, s=' | '.join([
            #     f'dd if={in_file} bs={chunk_size} skip={i} count=1 status=none',
            #     f'{patch_cmd.s} --data-binary -',
            # ]))
            # print(f'{patch_data_cmd.s=}')
            # patch_result = self._curl.run_cmd(patch_data_cmd, raise_=True)

            #

            with open(in_file, 'rb') as f:
                f.seek(ofs)
                buf = f.read(sz)
            with open(tmp_file, 'wb') as f:
                f.write(buf)
            num_written += len(buf)
            print(f'{num_written=}')
            patch_data_cmd = dc.replace(patch_cmd, s=f'{patch_cmd.s} --data-binary @{tmp_file}')
            print(f'{patch_data_cmd.s=}')
            patch_result = self._curl.run_cmd(patch_data_cmd, raise_=True)

            #

            check.equal(patch_result.status_code, 204)
            ofs += sz

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        commit_cmd = self._curl.build_post_json_cmd(
            f'caches/{cache_id}',
            GithubCacheServiceV1.dataclass_to_json(commit_req),
        )
        commit_result = self._curl.run_cmd(commit_cmd, raise_=True)
        check.equal(commit_result.status_code, 204)
