"""
TODO:
 - mirrors
 - huggingface_hub
 - stupid little progress bars
 - groups of multiple files downloaded - 'spec set'? idk
  - torchvision.datasets.FashionMNIST
 - chaining? or is this compcache..
 - download resume ala hf_hub
"""
import logging
import os.path
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from ... import git
from .actions import Action
from .actions import ExtractAction
from .manifests import Manifest
from .specs import GithubContentSpec
from .specs import GitSpec
from .specs import Spec
from .specs import UrlSpec


log = logging.getLogger(__name__)


##


class Cache:
    def __init__(self, base_dir: str) -> None:
        super().__init__()
        self._base_dir = base_dir

        self._items_dir = os.path.join(base_dir, 'items')

    #

    def _fetch_url(self, url: str, out_file: str) -> None:
        log.info('Fetching url: %s -> %s', url, out_file)

        urllib.request.urlretrieve(url, out_file)  # noqa

    def _fetch_into(self, spec: Spec, data_dir: str) -> None:
        log.info('Fetching spec: %s %r -> %s', spec.digest, spec, data_dir)

        if isinstance(spec, UrlSpec):
            self._fetch_url(spec.url, os.path.join(data_dir, spec.file_name_or_default))

        elif isinstance(spec, GithubContentSpec):
            for repo_file in spec.files:
                out_file = os.path.join(data_dir, repo_file)
                if not os.path.abspath(out_file).startswith(os.path.abspath(data_dir)):
                    raise RuntimeError(out_file)  # noqa

                url = f'https://raw.githubusercontent.com/{spec.repo}/{spec.rev}/{repo_file}'
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                self._fetch_url(url, os.path.join(data_dir, out_file))

        elif isinstance(spec, GitSpec):
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

    def _perform_action(self, action: Action, data_dir: str) -> None:
        if isinstance(action, ExtractAction):
            for f in action.files:
                file = os.path.join(data_dir, f)
                if not os.path.isfile(file):
                    raise Exception(f'Not file: {file}')

                if file.endswith('.tar.gz'):
                    subprocess.check_call(['tar', 'xzf', file], cwd=data_dir)

                else:
                    raise Exception(f'Unhandled archive extension: {file}')

                if not action.keep_archive:
                    os.unlink(file)

        else:
            raise TypeError(action)

    def _return_val(self, spec: Spec, data_dir: str) -> str:
        check.state(os.path.isdir(data_dir))

        if any(isinstance(a, ExtractAction) for a in spec.actions):
            return data_dir

        single_file: str
        if isinstance(spec, UrlSpec):
            single_file = os.path.join(data_dir, spec.file_name_or_default)

        elif isinstance(spec, GithubContentSpec):
            if len(spec.files) != 1:
                return data_dir
            single_file = os.path.join(data_dir, check.single(spec.files))

        else:
            return data_dir

        if not os.path.isfile(single_file):
            raise RuntimeError(single_file)  # noqa

        return single_file

    #

    def get(self, spec: Spec) -> str:
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
        for action in spec.actions:
            self._perform_action(action, fetch_dir)
        end_at = lang.utcnow()

        #

        manifest = Manifest(
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
