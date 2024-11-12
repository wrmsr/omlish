# ruff: noqa: UP007
# @omlish-lite
"""
git status
  --porcelain=v1
  --ignore-submodules
  2>/dev/null

==

In the short-format, the status of each path is shown as one of these forms

   XY PATH
   XY ORIG_PATH -> PATH

where ORIG_PATH is where the renamed/copied contents came from. ORIG_PATH is only shown when the entry is renamed or
copied. The XY is a two-letter status code.

The fields (including the ->) are separated from each other by a single space. If a filename contains whitespace or
other nonprintable characters, that field will be quoted in the manner of a C string literal: surrounded by ASCII double
quote (34) characters, and with interior special characters backslash-escaped.

There are three different types of states that are shown using this format, and each one uses the XY syntax differently:

 - When a merge is occurring and the merge was successful, or outside of a merge situation, X shows the status of the
   index and Y shows the status of the working tree.
 - When a merge conflict has occurred and has not yet been resolved, X and Y show the state introduced by each head of
   the merge, relative to the common ancestor. These paths are said to be unmerged.
 - When a path is untracked, X and Y are always the same, since they are unknown to the index.  ?? is used for untracked
   paths. Ignored files are not listed unless --ignored is used; if it is, ignored files are indicated by !!.

Note that the term merge here also includes rebases using the default --merge strategy, cherry-picks, and anything else
using the merge machinery.

In the following table, these three classes are shown in separate sections, and these characters are used for X and Y
fields for the first two sections that show tracked paths:

 - ' ' = unmodified
 - M = modified
 - T = file type changed (regular file, symbolic link or submodule)
 - A = added
 - D = deleted
 - R = renamed
 - C = copied (if config option status.renames is set to "copies")
 - U = updated but unmerged

X          Y     Meaning
-------------------------------------------------
         [AMD]   not updated
M        [ MTD]  updated in index
T        [ MTD]  type changed in index
A        [ MTD]  added to index
D                deleted from index
R        [ MTD]  renamed in index
C        [ MTD]  copied in index
[MTARC]          index and work tree matches
[ MTARC]    M    work tree changed since index
[ MTARC]    T    type changed in work tree since index
[ MTARC]    D    deleted in work tree
            R    renamed in work tree
            C    copied in work tree
-------------------------------------------------
D           D    unmerged, both deleted
A           U    unmerged, added by us
U           D    unmerged, deleted by them
U           A    unmerged, added by them
D           U    unmerged, deleted by us
A           A    unmerged, both added
U           U    unmerged, both modified
-------------------------------------------------
?           ?    untracked
!           !    ignored
-------------------------------------------------

Submodules have more state and instead report

 - M = the submodule has a different HEAD than recorded in the index
 - m = the submodule has modified content
 - ? = the submodule has untracked files

This is since modified content or untracked files in a submodule cannot be added via git add in the superproject to
prepare a commit.

m and ? are applied recursively. For example if a nested submodule in a submodule contains an untracked file, this is
reported as ? as well.

If -b is used the short-format status is preceded by a line

   ## branchname tracking info
"""
import os.path
import subprocess
import typing as ta

from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


def git_clone_subtree(
        *,
        base_dir: str,
        repo_url: str,
        repo_dir: str,
        branch: ta.Optional[str] = None,
        rev: ta.Optional[str] = None,
        repo_subtrees: ta.Sequence[str],
) -> None:
    if not bool(branch) ^ bool(rev):
        raise ValueError('must set branch or rev')

    if isinstance(repo_subtrees, str):
        raise TypeError(repo_subtrees)

    git_opts = [
        '-c', 'advice.detachedHead=false',
    ]

    subprocess.check_call(
        subprocess_maybe_shell_wrap_exec(
            'git',
            *git_opts,
            'clone',
            '-n',
            '--depth=1',
            '--filter=tree:0',
            *(['-b', branch] if branch else []),
            '--single-branch',
            repo_url,
            repo_dir,
        ),
        cwd=base_dir,
    )

    rd = os.path.join(base_dir, repo_dir)
    subprocess.check_call(
        subprocess_maybe_shell_wrap_exec(
            'git',
            *git_opts,
            'sparse-checkout',
            'set',
            '--no-cone',
            *repo_subtrees,
        ),
        cwd=rd,
    )

    subprocess.check_call(
        subprocess_maybe_shell_wrap_exec(
            'git',
            *git_opts,
            'checkout',
            *([rev] if rev else []),
        ),
        cwd=rd,
    )


def get_git_revision(
        *,
        cwd: ta.Optional[str] = None,
) -> ta.Optional[str]:
    subprocess.check_output(subprocess_maybe_shell_wrap_exec('git', '--version'))

    if cwd is None:
        cwd = os.getcwd()

    if subprocess.run(  # noqa
        subprocess_maybe_shell_wrap_exec(
            'git',
            'rev-parse',
            '--is-inside-work-tree',
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).returncode:
        return None

    has_untracked = bool(subprocess.check_output(subprocess_maybe_shell_wrap_exec(
        'git',
        'ls-files',
        '.',
        '--exclude-standard',
        '--others',
    ), cwd=cwd).decode().strip())

    dirty_rev = subprocess.check_output(subprocess_maybe_shell_wrap_exec(
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
    ), cwd=cwd).decode().strip()

    return dirty_rev + ('-untracked' if has_untracked else '')
