# @omlish-llm-author "gpt-5.4-thinking"
# @omlish-precheck-allow-any-unicode
import pytest

from ..parsing import DiffParseError
from ..parsing import apply_hunks_to_old_lines
from ..parsing import parse_patch
from ..parsing import reconstruct_file_pair_from_hunks
from ..types import BinaryFilesHeader
from ..types import DiffGitHeader
from ..types import ExtendedHeaderKind
from ..types import GitBinaryPatchHeader
from ..types import HunkLineKind
from ..types import IndexHeader
from ..types import ModeHeader
from ..types import PathHeader
from ..types import ScoreHeader


def test_parse_simple_modify_patch() -> None:
    diff_text = """\
diff --git a/foo.py b/foo.py
index 1910281..ba19a16 100644
--- a/foo.py
+++ b/foo.py
@@ -1,3 +1,4 @@
 import os
+import sys
 print("hello")
 x = 1
"""

    ps = parse_patch(diff_text)

    assert len(ps.files) == 1
    fp = ps.files[0]

    assert fp.old_path == 'foo.py'
    assert fp.new_path == 'foo.py'
    assert not fp.binary
    assert fp.added_count == 1
    assert fp.removed_count == 0

    assert isinstance(fp.extended_headers[0], DiffGitHeader)
    assert isinstance(fp.extended_headers[1], IndexHeader)

    h = fp.hunks[0]
    assert h.old_start == 1
    assert h.old_count == 3
    assert h.new_start == 1
    assert h.new_count == 4
    assert [ln.kind for ln in h.lines] == [
        HunkLineKind.CONTEXT,
        HunkLineKind.ADD,
        HunkLineKind.CONTEXT,
        HunkLineKind.CONTEXT,
    ]
    assert h.lines[1].text == 'import sys'


def test_parse_hunk_with_implicit_counts() -> None:
    diff_text = """\
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -3 +3 @@
-old
+new
"""

    ps = parse_patch(diff_text)
    h = ps.files[0].hunks[0]

    assert h.old_start == 3
    assert h.old_count == 1
    assert h.new_start == 3
    assert h.new_count == 1
    assert [ln.kind for ln in h.lines] == [
        HunkLineKind.REMOVE,
        HunkLineKind.ADD,
    ]


def test_parse_new_file_patch() -> None:
    diff_text = """\
diff --git a/dev/null b/newfile.txt
new file mode 100644
--- /dev/null
+++ b/newfile.txt
@@ -0,0 +1,2 @@
+hello
+world
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.is_new_file
    assert not fp.is_deleted_file
    assert fp.old_path is None
    assert fp.new_path == 'newfile.txt'
    assert fp.added_count == 2
    assert fp.removed_count == 0

    hdr = fp.extended_headers[1]
    assert isinstance(hdr, ModeHeader)
    assert hdr.kind == ExtendedHeaderKind.NEW_FILE_MODE
    assert hdr.mode == '100644'


def test_parse_deleted_file_patch() -> None:
    diff_text = """\
diff --git a/oldfile.txt b/dev/null
deleted file mode 100644
--- a/oldfile.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-old
-lines
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert not fp.is_new_file
    assert fp.is_deleted_file
    assert fp.old_path == 'oldfile.txt'
    assert fp.new_path is None
    assert fp.added_count == 0
    assert fp.removed_count == 2


def test_parse_rename_metadata() -> None:
    diff_text = """\
diff --git a/oldname.txt b/newname.txt
similarity index 98%
rename from oldname.txt
rename to newname.txt
--- a/oldname.txt
+++ b/newname.txt
@@ -1 +1 @@
-sameish
+sameish!
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.old_path == 'oldname.txt'
    assert fp.new_path == 'newname.txt'

    assert isinstance(fp.extended_headers[1], ScoreHeader)
    assert fp.extended_headers[1].score == 98

    assert isinstance(fp.extended_headers[2], PathHeader)
    assert fp.extended_headers[2].kind == ExtendedHeaderKind.RENAME_FROM
    assert fp.extended_headers[2].path == 'oldname.txt'

    assert isinstance(fp.extended_headers[3], PathHeader)
    assert fp.extended_headers[3].kind == ExtendedHeaderKind.RENAME_TO
    assert fp.extended_headers[3].path == 'newname.txt'


def test_parse_copy_metadata() -> None:
    diff_text = """\
diff --git a/src.txt b/dst.txt
similarity index 100%
copy from src.txt
copy to dst.txt
--- a/src.txt
+++ b/dst.txt
@@ -1 +1 @@
-line
+line
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.old_path == 'src.txt'
    assert fp.new_path == 'dst.txt'

    assert fp.extended_headers[2].kind == ExtendedHeaderKind.COPY_FROM
    assert fp.extended_headers[3].kind == ExtendedHeaderKind.COPY_TO


def test_parse_old_and_new_mode_headers() -> None:
    diff_text = """\
diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
--- a/script.sh
+++ b/script.sh
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert len(fp.hunks) == 0
    assert isinstance(fp.extended_headers[1], ModeHeader)
    assert fp.extended_headers[1].kind == ExtendedHeaderKind.OLD_MODE
    assert fp.extended_headers[1].mode == '100644'
    assert isinstance(fp.extended_headers[2], ModeHeader)
    assert fp.extended_headers[2].kind == ExtendedHeaderKind.NEW_MODE
    assert fp.extended_headers[2].mode == '100755'


def test_unknown_extended_header_is_preserved() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
weird vendor header xyz
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-a
+b
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.extended_headers[1].kind == ExtendedHeaderKind.UNKNOWN
    assert fp.extended_headers[1].text == 'weird vendor header xyz'


def test_parse_file_headers_with_timestamps() -> None:
    diff_text = """\
--- a/foo.txt\t2024-01-01 12:00:00 +0000
+++ b/foo.txt\t2024-01-02 12:00:00 +0000
@@ -1 +1 @@
-old
+new
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.old_file is not None
    assert fp.new_file is not None

    assert fp.old_file.path == 'foo.txt'
    assert fp.new_file.path == 'foo.txt'
    assert fp.old_file.timestamp == '2024-01-01 12:00:00 +0000'
    assert fp.new_file.timestamp == '2024-01-02 12:00:00 +0000'


def test_no_newline_marker_attaches_to_previous_removed_line() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-old
\\ No newline at end of file
+new
"""

    ps = parse_patch(diff_text)
    h = ps.files[0].hunks[0]

    assert len(h.lines) == 2
    assert h.lines[0].kind == HunkLineKind.REMOVE
    assert h.lines[0].has_no_newline_marker is True
    assert h.lines[1].kind == HunkLineKind.ADD
    assert h.lines[1].has_no_newline_marker is False


def test_no_newline_marker_attaches_to_previous_added_line() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -0,0 +1 @@
+new
\\ No newline at end of file
"""

    ps = parse_patch(diff_text)
    h = ps.files[0].hunks[0]

    assert len(h.lines) == 1
    assert h.lines[0].kind == HunkLineKind.ADD
    assert h.lines[0].has_no_newline_marker is True


def test_orphan_no_newline_marker_raises() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
\\ No newline at end of file
-old
+new
"""

    with pytest.raises(DiffParseError, match='orphaned no-newline marker'):
        parse_patch(diff_text)


def test_simple_binary_files_marker() -> None:
    diff_text = """\
diff --git a/a.png b/b.png
Binary files a/a.png and b/b.png differ
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.binary is True
    assert fp.git_binary_patch is None
    assert len(fp.hunks) == 0

    hdr = fp.extended_headers[1]
    assert isinstance(hdr, BinaryFilesHeader)
    assert hdr.old_path == 'a/a.png'
    assert hdr.new_path == 'b/b.png'

    # With only BinaryFilesHeader, old/new_path currently come directly from that header.
    assert fp.old_path == 'a.png'
    assert fp.new_path == 'b.png'


def test_git_binary_patch_payload_is_captured_and_not_decoded() -> None:
    diff_text = """\
diff --git a/img.png b/img.png
index 1111111..2222222 100644
GIT binary patch
literal 4
Oc${{m@<OaK000P11ONa4
literal 3
abc
diff --git a/next.txt b/next.txt
--- a/next.txt
+++ b/next.txt
@@ -1 +1 @@
-a
+b
"""

    ps = parse_patch(diff_text)

    assert len(ps.files) == 2

    fp0 = ps.files[0]
    assert fp0.binary is True
    assert fp0.git_binary_patch is not None
    assert isinstance(fp0.extended_headers[2], GitBinaryPatchHeader)
    assert fp0.git_binary_patch.lines == (
        'literal 4',
        'Oc${{m@<OaK000P11ONa4',
        'literal 3',
        'abc',
    )

    fp1 = ps.files[1]
    assert fp1.binary is False
    assert fp1.old_path == 'next.txt'


def test_hunk_old_count_mismatch_raises() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1,2 +1,1 @@
-old1
+new1
"""

    with pytest.raises(DiffParseError, match='old-count mismatch'):
        parse_patch(diff_text)


def test_hunk_new_count_mismatch_raises() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1,1 +1,2 @@
-old1
+new1
"""

    with pytest.raises(DiffParseError, match='new-count mismatch'):
        parse_patch(diff_text)


def test_missing_plus_plus_plus_header_raises() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
@@ -1 +1 @@
-old
+new
"""

    with pytest.raises(DiffParseError, match=r'expected \+\+\+ file header'):
        parse_patch(diff_text)


def test_apply_hunks_to_old_lines_simple_modify() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1,3 +1,4 @@
 a
+b
 c
 d
"""

    fp = parse_patch(diff_text).files[0]
    old_lines = ['a', 'c', 'd']

    out = apply_hunks_to_old_lines(fp, old_lines)

    assert out.path == 'foo.txt'
    assert out.lines == ('a', 'b', 'c', 'd')
    assert out.missing_trailing_newline is False


def test_apply_hunks_to_old_lines_rejects_context_mismatch() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1,2 +1,2 @@
 a
-b
+c
"""

    fp = parse_patch(diff_text).files[0]

    with pytest.raises(DiffParseError, match='remove mismatch'):
        apply_hunks_to_old_lines(fp, ['a', 'not-b'])


def test_apply_hunks_to_old_lines_rejects_binary_patch() -> None:
    diff_text = """\
diff --git a/a.png b/b.png
Binary files a/a.png and b/b.png differ
"""

    fp = parse_patch(diff_text).files[0]

    with pytest.raises(ValueError, match='cannot apply binary patch'):
        apply_hunks_to_old_lines(fp, [])


def test_reconstruct_file_pair_from_hunks_simple() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -2,3 +2,4 @@
 keep1
-old
+new
 keep2
+tail
"""

    fp = parse_patch(diff_text).files[0]
    pair = reconstruct_file_pair_from_hunks(fp)

    assert pair.before.path == 'foo.txt'
    assert pair.after.path == 'foo.txt'

    # Gap before hunk start is represented with placeholders.
    assert pair.before.lines == ('…', 'keep1', 'old', 'keep2')
    assert pair.after.lines == ('…', 'keep1', 'new', 'keep2', 'tail')


def test_reconstruct_file_pair_tracks_missing_trailing_newline() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-old
\\ No newline at end of file
+new
"""

    fp = parse_patch(diff_text).files[0]
    pair = reconstruct_file_pair_from_hunks(fp)

    assert pair.before.missing_trailing_newline is True
    assert pair.after.missing_trailing_newline is False


def test_multiple_file_patches_parse() -> None:
    diff_text = """\
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-a
+b
diff --git a/b.txt b/b.txt
--- a/b.txt
+++ b/b.txt
@@ -1 +1 @@
-x
+y
"""

    ps = parse_patch(diff_text)

    assert len(ps.files) == 2
    assert ps.files[0].old_path == 'a.txt'
    assert ps.files[1].old_path == 'b.txt'
    assert ps.added_count == 2
    assert ps.removed_count == 2


def test_patch_with_blank_lines_between_files_parses() -> None:
    diff_text = """\
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-a
+b

diff --git a/b.txt b/b.txt
--- a/b.txt
+++ b/b.txt
@@ -1 +1 @@
-x
+y
"""

    ps = parse_patch(diff_text)
    assert len(ps.files) == 2


def test_file_patch_with_no_hunks_but_headers_only_parses() -> None:
    diff_text = """\
diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
--- a/script.sh
+++ b/script.sh
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert len(fp.hunks) == 0
    assert fp.binary is False
    assert fp.old_path == 'script.sh'
    assert fp.new_path == 'script.sh'


def test_git_binary_patch_payload_lines_are_not_unknown_extended_headers() -> None:
    diff_text = """\
diff --git a/img.png b/img.png
index 1111111..2222222 100644
GIT binary patch
literal 4
Oc${{m@<OaK000P11ONa4
"""

    fp = parse_patch(diff_text).files[0]

    assert [h.kind for h in fp.extended_headers] == [
        ExtendedHeaderKind.DIFF_GIT,
        ExtendedHeaderKind.INDEX,
        ExtendedHeaderKind.GIT_BINARY_PATCH,
    ]
    assert fp.git_binary_patch is not None
    assert fp.git_binary_patch.lines == (
        'literal 4',
        'Oc${{m@<OaK000P11ONa4',
    )


def test_paths_with_spaces_and_backslashes() -> None:
    diff_text = """\
diff --git a/dir with spaces/odd\\name.txt b/dir with spaces/odd\\name.txt
--- a/dir with spaces/odd\\name.txt
+++ b/dir with spaces/odd\\name.txt
@@ -1 +1 @@
-old
+new
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.old_path == 'dir with spaces/odd\\name.txt'
    assert fp.new_path == 'dir with spaces/odd\\name.txt'
    assert fp.old_file is not None
    assert fp.new_file is not None
    assert fp.old_file.raw_path == 'a/dir with spaces/odd\\name.txt'
    assert fp.new_file.raw_path == 'b/dir with spaces/odd\\name.txt'


def test_rename_paths_with_spaces_and_backslashes() -> None:
    diff_text = """\
diff --git a/old dir/odd\\name.txt b/new dir/odd\\name.txt
rename from old dir/odd\\name.txt
rename to new dir/odd\\name.txt
--- a/old dir/odd\\name.txt
+++ b/new dir/odd\\name.txt
@@ -1 +1 @@
-old
+new
"""

    ps = parse_patch(diff_text)
    fp = ps.files[0]

    assert fp.old_path == 'old dir/odd\\name.txt'
    assert fp.new_path == 'new dir/odd\\name.txt'

    assert isinstance(fp.extended_headers[1], PathHeader)
    assert fp.extended_headers[1].kind == ExtendedHeaderKind.RENAME_FROM
    assert fp.extended_headers[1].path == 'old dir/odd\\name.txt'

    assert isinstance(fp.extended_headers[2], PathHeader)
    assert fp.extended_headers[2].kind == ExtendedHeaderKind.RENAME_TO
    assert fp.extended_headers[2].path == 'new dir/odd\\name.txt'


def test_git_binary_patch_payload_is_split_into_records() -> None:
    diff_text = """\
diff --git a/img.png b/img.png
index 1111111..2222222 100644
GIT binary patch
literal 4
Oc${{m@<OaK000P11ONa4
literal 3
abc
"""
    fp = parse_patch(diff_text).files[0]

    assert fp.git_binary_patch is not None
    assert len(fp.git_binary_patch.records) == 2

    r0, r1 = fp.git_binary_patch.records
    assert r0.kind == 'literal'
    assert r0.size == 4
    assert r0.payload_lines == ('Oc${{m@<OaK000P11ONa4',)

    assert r1.kind == 'literal'
    assert r1.size == 3
    assert r1.payload_lines == ('abc',)


def test_git_binary_patch_diff_git_inside_payload_is_hard_error() -> None:
    diff_text = """\
diff --git a/img.bin b/img.bin
index 1111111..2222222 100644
GIT binary patch
literal 4
diff --git a/not-really b/not-really
"""
    with pytest.raises(DiffParseError, match=r'has empty payload|no payload'):
        parse_patch(diff_text)


def test_git_binary_patch_blank_line_inside_payload_is_hard_error() -> None:
    diff_text = """\
diff --git a/img.bin b/img.bin
index 1111111..2222222 100644
GIT binary patch
literal 4

abc
"""
    with pytest.raises(DiffParseError, match=r'blank line inside git binary patch record|unexpected blank line'):
        parse_patch(diff_text)


def test_git_binary_patch_missing_record_header_is_hard_error() -> None:
    diff_text = """\
diff --git a/img.bin b/img.bin
index 1111111..2222222 100644
GIT binary patch
not-a-record
"""
    with pytest.raises(DiffParseError, match='expected git binary patch record'):
        parse_patch(diff_text)


def test_git_binary_patch_next_file_only_between_records() -> None:
    diff_text = """\
diff --git a/img.png b/img.png
index 1111111..2222222 100644
GIT binary patch
literal 4
Oc${{m@<OaK000P11ONa4
diff --git a/next.txt b/next.txt
--- a/next.txt
+++ b/next.txt
@@ -1 +1 @@
-a
+b
"""
    ps = parse_patch(diff_text)
    assert len(ps.files) == 2
    assert ps.files[0].git_binary_patch is not None
    assert ps.files[1].old_path == 'next.txt'


def test_parse_git_show_preamble() -> None:
    diff_text = """\
commit e66d283fc6b0827d51191aacfbcec810b70ce2fd
Author: Test User <test@example.com>
Date:   Thu Mar 12 12:34:56 2026 -0700

    Example commit message

diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-old
+new
"""
    ps = parse_patch(diff_text)
    assert len(ps.files) == 1
    assert ps.files[0].old_path == 'foo.txt'


def test_parse_format_patch_preamble() -> None:
    diff_text = """\
From e66d283fc6b0827d51191aacfbcec810b70ce2fd Mon Sep 17 00:00:00 2001
From: Test User <test@example.com>
Date: Thu, 12 Mar 2026 12:34:56 -0700
Subject: [PATCH] Example patch

---
 foo.txt | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-old
+new
"""
    ps = parse_patch(diff_text)
    assert len(ps.files) == 1
    assert ps.files[0].new_path == 'foo.txt'
