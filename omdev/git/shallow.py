# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import os.path
import typing as ta

from omlish.subprocesses.sync import subprocesses


@dc.dataclass(frozen=True)
class GitShallowCloner:
    base_dir: str
    repo_url: str
    repo_dir: str

    # _: dc.KW_ONLY

    repo_subtrees: ta.Optional[ta.Sequence[str]] = None

    branch: ta.Optional[str] = None
    rev: ta.Optional[str] = None

    def __post_init__(self) -> None:
        if not bool(self.branch) ^ bool(self.rev):
            raise ValueError('must set branch or rev')

        if isinstance(self.repo_subtrees, str):
            raise TypeError(self.repo_subtrees)

    @dc.dataclass(frozen=True)
    class Command:
        cmd: ta.Sequence[str]
        cwd: str

    def build_commands(self) -> ta.Iterator[Command]:
        git_opts = [
            '-c', 'advice.detachedHead=false',
        ]

        yield GitShallowCloner.Command(
            cmd=(
                'git',
                *git_opts,
                'clone',
                '-n',
                '--depth=1',
                '--filter=tree:0',
                *(['-b', self.branch] if self.branch else []),
                '--single-branch',
                self.repo_url,
                self.repo_dir,
            ),
            cwd=self.base_dir,
        )

        rd = os.path.join(self.base_dir, self.repo_dir)
        if self.repo_subtrees is not None:
            yield GitShallowCloner.Command(
                cmd=(
                    'git',
                    *git_opts,
                    'sparse-checkout',
                    'set',
                    '--no-cone',
                    *self.repo_subtrees,
                ),
                cwd=rd,
            )

        yield GitShallowCloner.Command(
            cmd=(
                'git',
                *git_opts,
                'checkout',
                *([self.rev] if self.rev else []),
            ),
            cwd=rd,
        )


def git_shallow_clone(
        *,
        base_dir: str,
        repo_url: str,
        repo_dir: str,
        branch: ta.Optional[str] = None,
        rev: ta.Optional[str] = None,
        repo_subtrees: ta.Optional[ta.Sequence[str]] = None,
) -> None:
    for cmd in GitShallowCloner(
        base_dir=base_dir,
        repo_url=repo_url,
        repo_dir=repo_dir,
        branch=branch,
        rev=rev,
        repo_subtrees=repo_subtrees,
    ).build_commands():
        subprocesses.check_call(
            *cmd.cmd,
            cwd=cmd.cwd,
        )
