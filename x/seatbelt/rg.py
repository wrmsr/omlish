"""
log stream --style compact --predicate 'sender=="Sandbox"'

====

(version 1)

(deny default)

;; argv/env/process/runtime basics
(allow sysctl-read)
(allow process-info*)
(allow signal (target self))

;; Only allow exec of rg itself.
(allow process-exec
  (literal (param "RG_BIN")))

;; macOS runtime lookups that many CLI tools may touch indirectly.
;; Keep this list small; add only from sandboxd logs.
(allow mach-lookup
  (global-name "com.apple.system.opendirectoryd.libinfo")
  (global-name "com.apple.coreservices.launchservicesd"))

;; Metadata generally leaks much less than data, and avoids tons of
;; path-resolution / stat failures. If this is too broad for your taste,
;; narrow it later after the thing works.
(allow file-read-metadata)

;; Dynamic loader / system runtime reads.
(allow file-read-data
  (subpath "/System/Library")
  (subpath "/usr/lib")
  (subpath "/usr/share")
  (subpath "/private/var/db")
  (literal "/dev/null")
  (literal (param "RG_BIN"))
  (subpath (param "RG_DIR")))

;; Homebrew case, if applicable.
;; For first debug pass, allow the rg prefix; later narrow to exact dylib dirs.
(allow file-read-data
  (subpath "/opt/homebrew")
  (subpath "/usr/local"))

;; Allowed search roots. Generate these.
;; (allow file-read* (literal (param "ROOT_0")))
;; (allow file-read* (subpath (param "ROOT_0")))
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import typing as ta


def _realpath(p: str | os.PathLike[str]) -> str:
    return os.path.realpath(os.path.abspath(os.fspath(p)))


def _ancestor_dirs(path: str) -> list[str]:
    p = pathlib.Path(path)
    # For /Users/me/src/repo -> ["/", "/Users", "/Users/me", "/Users/me/src"]
    return [str(x) for x in reversed(p.parents)]


def _under(path: str, root: str) -> bool:
    path = _realpath(path)
    root = _realpath(root)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def sandboxed_rg(
    pattern: str,
    roots: ta.Sequence[str | os.PathLike[str]],
    *,
    rg_args: ta.Sequence[str] = (),
    timeout: float = 30.0,
) -> subprocess.CompletedProcess[str]:
    """
    rg_args should be your own allowlisted flags, not arbitrary model-supplied text.
    """

    if not roots:
        raise ValueError("at least one allowed root is required")

    rg0 = shutil.which("rg")
    if rg0 is None:
        raise FileNotFoundError("rg not found on PATH")

    rg = _realpath(rg0)
    roots_real = [_realpath(r) for r in roots]

    for r in roots_real:
        if not os.path.isdir(r):
            raise NotADirectoryError(r)

    # Minimal-ish runtime read set. You can tighten this after seeing sandboxd logs.
    tool_read_roots = [
        "/System/Library",
        "/usr/lib",
        "/usr/share",
        os.path.dirname(rg),
    ]

    if rg.startswith("/opt/homebrew/"):
        tool_read_roots.append("/opt/homebrew")
    elif rg.startswith("/usr/local/"):
        tool_read_roots.extend(["/usr/local/Cellar", "/usr/local/opt", "/usr/local/lib"])
    elif rg.startswith("/opt/local/"):
        tool_read_roots.append("/opt/local")

    profile_lines = [
        "(version 1)",
        "(deny default)",
        '(allow process-exec (literal (param "RG_BIN")))',
        "(allow sysctl-read)",
        '(allow file-read* file-test-existence (literal "/"))',
        "(allow file-read*",
    ]

    param_defs: list[str] = [
        f"RG_BIN={rg}",
        f"RG_DIR={os.path.dirname(rg)}",
    ]

    for i, tr in enumerate(dict.fromkeys(tool_read_roots)):
        if os.path.exists(tr):
            key = f"TOOL_READ_{i}"
            param_defs.append(f"{key}={tr}")
            profile_lines.append(f'  (subpath (param "{key}"))')

    profile_lines.append(")")

    # Allow ancestor metadata for path resolution, but not directory contents.
    ancestor_params: list[str] = []
    seen_ancestors: set[str] = set()
    for r in roots_real:
        for a in _ancestor_dirs(r):
            if a not in seen_ancestors:
                seen_ancestors.add(a)
                key = f"ANCESTOR_{len(ancestor_params)}"
                ancestor_params.append(key)
                param_defs.append(f"{key}={a}")

    if ancestor_params:
        profile_lines.append("(allow file-read-metadata")
        for key in ancestor_params:
            profile_lines.append(f'  (literal (param "{key}"))')
        profile_lines.append(")")

    # Allow the actual requested roots.
    for i, r in enumerate(roots_real):
        key = f"ROOT_{i}"
        param_defs.append(f"{key}={r}")
        profile_lines.append(f'(allow file-read* (literal (param "{key}")))')
        profile_lines.append(f'(allow file-read* (subpath (param "{key}")))')

    profile = "\n".join(profile_lines) + "\n"

    defs: list[str] = []
    for d in param_defs:
        defs.extend(["-D", d])

    # These are defense-in-depth against rg features that read surprising places
    # or spawn helper programs.
    safety_rg_args = [
        "--no-config",
        "--no-pre",
        "--no-search-zip",
        "--no-follow",
        "--no-ignore-parent",
        "--no-ignore-global",
        "--color=never",
    ]

    cmd = [
        "/usr/bin/sandbox-exec",
        *defs,
        "-p",
        profile,
        rg,
        *rg_args,
        *safety_rg_args,
        "-e",
        pattern,
        "--",
        *roots_real,
    ]

    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": "/var/empty",
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", os.environ.get("LANG", "C.UTF-8")),
    }

    return subprocess.run(
        cmd,
        cwd=roots_real[0],
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        close_fds=True,
        check=False,
    )


def _main() -> None:
    out = sandboxed_rg(
        'foo',
        ['omlish'],
    )

    print(out)


if __name__ == '__main__':
    _main()