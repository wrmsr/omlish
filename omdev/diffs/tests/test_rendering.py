from ..parsing import parse_patch
from ..rendering import PatchRenderOptions
from ..rendering import PatchSetRenderer
from ..types import BinaryFilesHeader
from ..types import ExtendedHeader
from ..types import ExtendedHeaderKind
from ..types import FileHeader
from ..types import GitBinaryPatchHeader
from ..types import HunkLine
from ..types import HunkLineKind


def _roundtrip(diff_text: str):
    parsed = parse_patch(diff_text)
    rendered = PatchSetRenderer().render_patch_set(parsed)
    reparsed = parse_patch(rendered)
    return parsed, rendered, reparsed


def test_render_roundtrip_simple_modify_patch() -> None:
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

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'diff --git a/foo.py b/foo.py\n' in rendered
    assert 'index 1910281..ba19a16 100644\n' in rendered
    assert '@@ -1,3 +1,4 @@\n' in rendered
    assert '+import sys\n' in rendered


def test_render_roundtrip_new_file_patch() -> None:
    diff_text = """\
diff --git a/dev/null b/newfile.txt
new file mode 100644
--- /dev/null
+++ b/newfile.txt
@@ -0,0 +1,2 @@
+hello
+world
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'new file mode 100644\n' in rendered
    assert '--- /dev/null\n' in rendered
    assert '+++ b/newfile.txt\n' in rendered


def test_render_roundtrip_deleted_file_patch() -> None:
    diff_text = """\
diff --git a/oldfile.txt b/dev/null
deleted file mode 100644
--- a/oldfile.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-old
-lines
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'deleted file mode 100644\n' in rendered
    assert '--- a/oldfile.txt\n' in rendered
    assert '+++ /dev/null\n' in rendered


def test_render_roundtrip_rename_patch() -> None:
    diff_text = """\
diff --git a/oldname.txt b/newname.txt
similarity index 98%
rename from oldname.txt
rename to newname.txt
--- a/oldname.txt
+++ b/newname.txt
@@ -1 +1 @@
-old
+new
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'similarity index 98%\n' in rendered
    assert 'rename from oldname.txt\n' in rendered
    assert 'rename to newname.txt\n' in rendered


def test_render_roundtrip_copy_patch() -> None:
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

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'copy from src.txt\n' in rendered
    assert 'copy to dst.txt\n' in rendered


def test_render_roundtrip_mode_change_only_patch() -> None:
    diff_text = """\
diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
--- a/script.sh
+++ b/script.sh
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'old mode 100644\n' in rendered
    assert 'new mode 100755\n' in rendered
    assert rendered.endswith('+++ b/script.sh\n')


def test_render_roundtrip_unknown_extended_header() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
weird vendor header xyz
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-a
+b
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'weird vendor header xyz\n' in rendered


def test_render_roundtrip_file_headers_with_timestamps() -> None:
    diff_text = """\
--- a/foo.txt\t2024-01-01 12:00:00 +0000
+++ b/foo.txt\t2024-01-02 12:00:00 +0000
@@ -1 +1 @@
-old
+new
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert '--- a/foo.txt\t2024-01-01 12:00:00 +0000\n' in rendered
    assert '+++ b/foo.txt\t2024-01-02 12:00:00 +0000\n' in rendered


def test_render_roundtrip_no_newline_marker_on_removed_line() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-old
\\ No newline at end of file
+new
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert '\\ No newline at end of file\n' in rendered


def test_render_roundtrip_no_newline_marker_on_added_line() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -0,0 +1 @@
+new
\\ No newline at end of file
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert rendered.count('\\ No newline at end of file\n') == 1


def test_render_roundtrip_binary_files_marker() -> None:
    diff_text = """\
diff --git a/a.png b/b.png
Binary files a/a.png and b/b.png differ
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'Binary files a/a.png and b/b.png differ\n' in rendered


def test_render_roundtrip_git_binary_patch() -> None:
    diff_text = """\
diff --git a/img.png b/img.png
index 1111111..2222222 100644
GIT binary patch
literal 4
Oc${{m@<OaK000P11ONa4
literal 3
abc
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'GIT binary patch\n' in rendered
    assert 'literal 4\n' in rendered
    assert 'Oc${{m@<OaK000P11ONa4\n' in rendered
    assert 'literal 3\n' in rendered
    assert 'abc\n' in rendered


def test_render_roundtrip_multiple_file_patches() -> None:
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

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert rendered.count('diff --git ') == 2


def test_render_trailing_newline_option_false() -> None:
    diff_text = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1 +1 @@
-old
+new
"""

    parsed = parse_patch(diff_text)
    rendered = PatchSetRenderer(PatchRenderOptions(trailing_newline=False)).render_patch_set(parsed)

    assert rendered.endswith('+new\n')
    assert not rendered.endswith('\n\n')


def test_render_hunk_header_omits_count_when_one() -> None:
    diff_text = """\
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -3 +3 @@
-old
+new
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert '@@ -3 +3 @@\n' in rendered


def test_render_hunk_header_includes_section_text() -> None:
    diff_text = """\
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -10,2 +10,3 @@ some section heading
 old1
-old2
+new2
+new3
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert '@@ -10,2 +10,3 @@ some section heading\n' in rendered


def test_render_paths_with_spaces_and_backslashes() -> None:
    diff_text = """\
diff --git a/dir with spaces/odd\\name.txt b/dir with spaces/odd\\name.txt
--- a/dir with spaces/odd\\name.txt
+++ b/dir with spaces/odd\\name.txt
@@ -1 +1 @@
-old
+new
"""

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'diff --git a/dir with spaces/odd\\name.txt b/dir with spaces/odd\\name.txt\n' in rendered
    assert '--- a/dir with spaces/odd\\name.txt\n' in rendered
    assert '+++ b/dir with spaces/odd\\name.txt\n' in rendered


def test_render_rename_paths_with_spaces_and_backslashes() -> None:
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

    parsed, rendered, reparsed = _roundtrip(diff_text)

    assert reparsed == parsed
    assert 'rename from old dir/odd\\name.txt\n' in rendered
    assert 'rename to new dir/odd\\name.txt\n' in rendered


def test_render_unknown_extended_header_directly() -> None:
    renderer = PatchSetRenderer()

    hdr = ExtendedHeader(
        kind=ExtendedHeaderKind.UNKNOWN,
        text='strange custom header',
        span=None,  # type: ignore[arg-type]
    )

    assert renderer.render_extended_header(hdr) == 'strange custom header\n'


def test_render_binary_files_header_directly() -> None:
    renderer = PatchSetRenderer()

    hdr = BinaryFilesHeader(
        kind=ExtendedHeaderKind.BINARY_FILES,
        text='Binary files a/a.bin and b/b.bin differ',
        span=None,  # type: ignore[arg-type]
        old_path='a/a.bin',
        new_path='b/b.bin',
    )

    assert renderer.render_extended_header(hdr) == 'Binary files a/a.bin and b/b.bin differ\n'


def test_render_git_binary_patch_header_directly() -> None:
    renderer = PatchSetRenderer()

    hdr = GitBinaryPatchHeader(
        kind=ExtendedHeaderKind.GIT_BINARY_PATCH,
        text='GIT binary patch',
        span=None,  # type: ignore[arg-type]
    )

    assert renderer.render_extended_header(hdr) == 'GIT binary patch\n'


def test_render_file_header_directly() -> None:
    renderer = PatchSetRenderer()

    hdr = FileHeader(
        prefix='---',
        path='foo.txt',
        timestamp='2024-01-01 00:00:00 +0000',
        raw_path='a/foo.txt',
        text='--- a/foo.txt\t2024-01-01 00:00:00 +0000',
        span=None,  # type: ignore[arg-type]
    )

    assert renderer.render_file_header(hdr) == '--- a/foo.txt\t2024-01-01 00:00:00 +0000\n'


def test_render_hunk_line_directly() -> None:
    renderer = PatchSetRenderer()

    assert renderer.render_hunk_line(HunkLine(
        kind=HunkLineKind.CONTEXT,
        text='ctx',
        span=None,
    )) == ' ctx\n'
    assert renderer.render_hunk_line(HunkLine(
        kind=HunkLineKind.ADD,
        text='add',
        span=None,
    )) == '+add\n'
    assert renderer.render_hunk_line(HunkLine(
        kind=HunkLineKind.REMOVE,
        text='rm',
        span=None,
    )) == '-rm\n'


def test_render_roundtrip_with_preamble() -> None:
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

    parsed = parse_patch(diff_text)
    rendered = PatchSetRenderer().render_patch_set(parsed)
    reparsed = parse_patch(rendered)

    assert reparsed == parsed
