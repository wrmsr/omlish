"""
TODO:
 - huggingface_hub
 - postprocessing?
  - unarchive
 - stupid little progress bars
 - return file path for single files
  - thus, HttpSpec.url has derive=lambda url: ...
"""
import logging
import os.path
import shutil
import tempfile
import urllib.parse
import urllib.request

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from .. import git
from .manifests import CacheDataManifest
from .specs import CacheDataSpec
from .specs import GitCacheDataSpec
from .specs import GithubContentCacheDataSpec
from .specs import HttpCacheDataSpec


log = logging.getLogger(__name__)


##


class DataCache:
    def __init__(self, base_dir: str) -> None:
        super().__init__()
        self._base_dir = base_dir

        self._items_dir = os.path.join(base_dir, 'items')

    def _fetch_url(self, url: str, out_file: str) -> None:
        log.info('Fetching url: %s -> %s', url, out_file)

        urllib.request.urlretrieve(url, out_file)  # noqa

    def _fetch_into(self, spec: CacheDataSpec, data_dir: str) -> None:
        log.info('Fetching spec: %s %r -> %s', spec.digest, spec, data_dir)

        if isinstance(spec, HttpCacheDataSpec):
            self._fetch_url(spec.url, os.path.join(data_dir, spec.file_name_or_default))

        elif isinstance(spec, GithubContentCacheDataSpec):
            for repo_file in spec.files:
                out_file = os.path.join(data_dir, repo_file)
                if not os.path.abspath(out_file).startswith(os.path.abspath(data_dir)):
                    raise RuntimeError(out_file)  # noqa

                url = f'https://raw.githubusercontent.com/{spec.repo}/{spec.rev}/{repo_file}'
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                self._fetch_url(url, os.path.join(data_dir, out_file))

        elif isinstance(spec, GitCacheDataSpec):
            if not spec.subtrees:
                raise NotImplementedError

            tmp_dir = tempfile.mkdtemp()

            log.info('Cloning git repo: %s -> %s', spec.url, tmp_dir)

            git.git_clone_subtree(
                base_dir=tmp_dir,
                repo_url=spec.url,
                repo_dir='data',
                branch=spec.branch,
                rev=spec.rev,
                repo_subtrees=spec.subtrees,
            )

            repo_dir = os.path.join(tmp_dir, 'data')
            if not os.path.isdir(repo_dir):
                raise RuntimeError(repo_dir)

            git_dir = os.path.join(repo_dir, '.git')
            if not os.path.isdir(git_dir):
                raise RuntimeError(git_dir)
            shutil.rmtree(git_dir)

            os.rmdir(data_dir)
            os.rename(repo_dir, data_dir)

        else:
            raise TypeError(spec)

    def _return_val(self, spec: CacheDataSpec, data_dir: str) -> str:
        check.state(os.path.isdir(data_dir))

        if isinstance(spec, HttpCacheDataSpec):
            data_file = os.path.join(data_dir, spec.file_name_or_default)
            if not os.path.isfile(data_file):
                raise RuntimeError(data_file)  # noqa
            return data_file

        elif isinstance(spec, GithubContentCacheDataSpec):
            if len(spec.files) != 1:
                return data_dir
            data_file = os.path.join(data_dir, check.single(spec.files))
            if not os.path.isfile(data_file):
                raise RuntimeError(data_file)  # noqa
            return data_file

        else:
            return data_dir

    def get(self, spec: CacheDataSpec) -> str:
        os.makedirs(self._items_dir, exist_ok=True)

        #

        item_dir = os.path.join(self._items_dir, spec.digest)
        if os.path.isdir(item_dir):
            data_dir = os.path.join(item_dir, 'data')
            return self._return_val(spec, data_dir)

        #

        tmp_dir = tempfile.mkdtemp()

        #

        fetch_dir = os.path.join(tmp_dir, 'data')
        os.mkdir(fetch_dir)

        start_at = lang.utcnow()
        self._fetch_into(spec, fetch_dir)
        end_at = lang.utcnow()

        #

        manifest = CacheDataManifest(
            spec,
            start_at=start_at,
            end_at=end_at,
        )
        manifest_json = json.dumps_pretty(msh.marshal(manifest))

        manifest_file = os.path.join(tmp_dir, 'manifest.json')
        with open(manifest_file, 'w') as f:
            f.write(manifest_json)

        #

        # for p, ds, fs in os.walk(tmp_dir):
        #     for n in [*ds, *fs]:
        #         np = os.path.join(p, n)
        #         os.chmod(np, os.stat(np).st_mode & ~0o222)

        #

        shutil.move(tmp_dir, item_dir)

        data_dir = os.path.join(item_dir, 'data')
        return self._return_val(spec, data_dir)
