# @omlish-llm-author gemini-2.5-pro
import re
import textwrap

import pytest

from ..applypatch import ActionType
from ..applypatch import Chunk
from ..applypatch import DiffError
from ..applypatch import Parser
from ..applypatch import Patch
from ..applypatch import PatchAction
from ..applypatch import _get_updated_file
from ..applypatch import find_context
from ..applypatch import identify_files_added
from ..applypatch import identify_files_needed
from ..applypatch import patch_to_commit
from ..applypatch import peek_next_section
from ..applypatch import text_to_patch


# Helper to create Parser instances easily
def make_parser(patch_lines, current_files=None, index=1):
    if current_files is None:
        current_files = {}
    return Parser(
        current_files=current_files,
        lines=patch_lines,
        index=index,
    )


##
# Tests for Parser


class TestParser:
    def test_norm_crlf(self):
        assert Parser.norm('line\r') == 'line'
        assert Parser.norm('line') == 'line'

    def test_cur_line(self):
        parser = make_parser(['line1', 'line2'], index=0)
        assert parser._cur_line() == 'line1'  # noqa
        parser.index = 1
        assert parser._cur_line() == 'line2'  # noqa

    def test_cur_line_out_of_bounds(self):
        parser = make_parser(['line1'], index=1)
        with pytest.raises(DiffError, match='Unexpected end of input'):
            parser._cur_line()  # noqa

    def test_is_done(self):
        parser = make_parser(['line1', '*** End Patch'], index=0)
        assert not parser.is_done()
        parser.index = 1
        assert parser.is_done(('*** End Patch',))
        parser.index = 2
        assert parser.is_done()

    def test_startswith(self):
        parser = make_parser(['*** Update File: file.txt'], index=0)
        assert parser.startswith('*** Update File:')
        assert not parser.startswith('---')

    def test_read_str(self):
        parser = make_parser(['prefix text', 'another line'], index=0)
        assert parser.read_str('prefix ') == 'text'
        assert parser.index == 1
        assert parser.read_str('non_existent_prefix') == ''  # Does not advance
        assert parser.index == 1

    def test_read_str_empty_prefix(self):
        parser = make_parser(['line'], index=0)
        with pytest.raises(ValueError, match=re.escape('read_str() requires a non-empty prefix')):
            parser.read_str('')

    def test_read_line(self):
        parser = make_parser(['line1\r\n', 'line2'], index=0)
        assert parser.read_line() == 'line1\r\n'
        assert parser.index == 1
        assert parser.read_line() == 'line2'
        assert parser.index == 2

    def test_parse_simple_add(self):
        patch_text = [
            '*** Begin Patch',
            '*** Add File: new.txt',
            '+Hello',
            '+World',
            '*** End Patch',
        ]
        parser = make_parser(patch_text, current_files={})
        parser.parse()
        assert 'new.txt' in parser.patch.actions
        action = parser.patch.actions['new.txt']
        assert action.type == ActionType.ADD
        assert action.new_file == 'Hello\nWorld'

    def test_parse_simple_delete(self):
        patch_text = [
            '*** Begin Patch',
            '*** Delete File: old.txt',
            '*** End Patch',
        ]
        current_files = {'old.txt': 'content'}
        parser = make_parser(patch_text, current_files=current_files)
        parser.parse()
        assert 'old.txt' in parser.patch.actions
        action = parser.patch.actions['old.txt']
        assert action.type == ActionType.DELETE

    def test_parse_simple_update(self):
        patch_text = [
            '*** Begin Patch',
            '*** Update File: existing.txt',
            '@@ Line 1',
            '-Line 2',
            '+Line Two',
            ' Line 3',
            '*** End Patch',
        ]
        current_files = {'existing.txt': 'Line 1\nLine 2\nLine 3'}
        parser = make_parser(patch_text, current_files=current_files)
        parser.parse()
        assert 'existing.txt' in parser.patch.actions
        action = parser.patch.actions['existing.txt']
        assert action.type == ActionType.UPDATE
        assert len(action.chunks) == 1
        chunk = action.chunks[0]
        assert chunk.del_lines == ['Line 2']
        assert chunk.ins_lines == ['Line Two']
        assert chunk.orig_index == 1  # After "Line 1"

    def test_parse_simple_update_first_line(self):
        patch_text = [
            '*** Begin Patch',
            '*** Update File: existing.txt',
            '@@',
            '-Line 1',
            '+Line one',
            ' Line 2',
            ' Line 3',
            '*** End Patch',
        ]
        current_files = {'existing.txt': 'Line 1\nLine 2\nLine 3'}
        parser = make_parser(patch_text, current_files=current_files)
        parser.parse()
        assert 'existing.txt' in parser.patch.actions
        action = parser.patch.actions['existing.txt']
        assert action.type == ActionType.UPDATE
        assert len(action.chunks) == 1
        chunk = action.chunks[0]
        assert chunk.del_lines == ['Line 1']
        assert chunk.ins_lines == ['Line one']
        assert chunk.orig_index == 0

    def test_parse_update_with_move(self):
        patch_text = [
            '*** Begin Patch',
            '*** Update File: old.txt',
            '*** Move to: new.txt',
            '@@',
            '-Old content',
            '+New content',
            '*** End Patch',
        ]
        current_files = {'old.txt': 'Old content'}
        parser = make_parser(patch_text, current_files=current_files)
        parser.parse()
        action = parser.patch.actions['old.txt']
        assert action.type == ActionType.UPDATE
        assert action.move_path == 'new.txt'

    def test_parse_duplicate_add(self):
        patch_text = [
            '*** Begin Patch',
            '*** Add File: new.txt',
            '+content',
            '*** Add File: new.txt',
            '+content2',
            '*** End Patch',
        ]
        parser = make_parser(patch_text, current_files={})
        with pytest.raises(DiffError, match=re.escape('Duplicate add for file: new.txt')):
            parser.parse()

    def test_parse_add_existing_file(self):
        patch_text = [
            '*** Begin Patch',
            '*** Add File: exists.txt',
            '+content',
            '*** End Patch',
        ]
        parser = make_parser(patch_text, current_files={'exists.txt': ''})
        with pytest.raises(DiffError, match=re.escape('Add File Error - file already exists: exists.txt')):
            parser.parse()

    def test_parse_delete_missing_file(self):
        patch_text = [
            '*** Begin Patch',
            '*** Delete File: missing.txt',
            '*** End Patch',
        ]
        parser = make_parser(patch_text, current_files={})
        with pytest.raises(DiffError, match=re.escape('Delete File Error - missing file: missing.txt')):
            parser.parse()

    def test_parse_update_missing_file(self):
        patch_text = [
            '*** Begin Patch',
            '*** Update File: missing.txt',
            '@@ context',
            '*** End Patch',
        ]
        parser = make_parser(patch_text, current_files={})
        with pytest.raises(DiffError, match=re.escape('Update File Error - missing file: missing.txt')):
            parser.parse()

    def test_parse_unknown_line(self):
        patch_text = [
            '*** Begin Patch',
            '*** Unknown Command: file.txt',
            '*** End Patch',
        ]
        parser = make_parser(patch_text, current_files={})
        with pytest.raises(DiffError, match='Unknown line while parsing:'):
            parser.parse()

    def test_parse_missing_end_patch(self):
        patch_text = [
            '*** Begin Patch',
            '*** Add File: new.txt',
            '+Hello',
        ]
        parser = make_parser(patch_text, current_files={})
        with pytest.raises(DiffError):
            parser.parse()

    def test_parse_add_file_invalid_line(self):
        patch_text = [
            '*** Begin Patch',
            '*** Add File: new.txt',
            'Invalid line',
            '*** End Patch',
        ]
        parser = make_parser(patch_text)
        with pytest.raises(DiffError, match=re.escape("Invalid Add File line (missing '+'): Invalid line")):
            parser.parse()

    def test_parse_update_file_invalid_line(self):
        patch_text = [
            '*** Begin Patch',
            '*** Update File: existing.txt',
            'Invalid line in update',
            '*** End Patch',
        ]
        current_files = {'existing.txt': 'Line 1\nLine 2'}
        parser = make_parser(patch_text, current_files=current_files)
        with pytest.raises(DiffError, match=re.escape('Invalid Line: Invalid line in update')):
            parser.parse()

    def test_parse_update_file_context_not_found(self):
        patch_text = [
            '*** Begin Patch',
            '*** Update File: existing.txt',
            '@@ NonExistentContext',
            ' Line 1',
            '*** End Patch',
        ]
        current_files = {'existing.txt': 'Line 1\nLine 2'}
        parser = make_parser(patch_text, current_files=current_files)
        with pytest.raises(DiffError, match=re.escape('Invalid context at 0:\nNonExistentContext')):
            parser.parse()


##
# Tests for find_context


@pytest.mark.parametrize(
    ('lines', 'context', 'start', 'eof', 'expected_index', 'expected_fuzz'),
    [
        (['a', 'b', 'c', 'd'], ['b', 'c'], 0, False, 1, 0),
        (['a', 'b ', 'c ', 'd'], ['b', 'c'], 0, False, 1, 1),  # rstrip
        (['a', ' b ', ' c ', 'd'], ['b', 'c'], 0, False, 1, 100),  # strip
        (['a', 'b', 'c', 'd'], ['x', 'y'], 0, False, -1, 0),  # not found
        (['a', 'b', 'c'], [], 0, False, 0, 0),  # empty context
        (['a', 'b', 'c', 'x', 'y'], ['x', 'y'], 0, True, 3, 0),  # eof, found at end
        # (['x', 'y', 'a', 'b', 'c'], ['x', 'y'], 2, True, 0, 10000),  # eof, found at start after initial check fails
        (['a', 'b', 'c'], ['x', 'y'], 0, True, -1, 10000),  # eof, not found
    ],
)
def test_find_context(lines, context, start, eof, expected_index, expected_fuzz):
    result = find_context(lines, context, start, eof)
    assert result.new_index == expected_index
    assert result.fuzz == expected_fuzz


##
# Tests for peek_next_section


def test_peek_next_section_simple():
    lines = [
        ' Line 1',
        '-Line 2',
        '+Line Two',
        ' Line 3',
        '@@ Next section',
    ]
    section, chunks, idx, eof = peek_next_section(lines, 0)
    assert section == ['Line 1', 'Line 2', 'Line 3']
    assert len(chunks) == 1
    assert chunks[0].del_lines == ['Line 2']
    assert chunks[0].ins_lines == ['Line Two']
    assert chunks[0].orig_index == 1  # after "Line 1"
    assert idx == 4  # points to "@@ Next section"
    assert not eof


def test_peek_next_section_empty_line_as_space():
    lines = [
        '',  # becomes " "
        '+Added',
        '@@ Next section',
    ]
    section, chunks, idx, eof = peek_next_section(lines, 0)
    assert section == ['']  # Note: " " is from the empty line
    assert len(chunks) == 1
    assert chunks[0].del_lines == []
    assert chunks[0].ins_lines == ['Added']
    assert chunks[0].orig_index == 1  # After the " " context
    assert idx == 2
    assert not eof


def test_peek_next_section_multiple_chunks():
    lines = [
        '-Del1',
        '+Add1',
        ' Keep1',
        '-Del2',
        '+Add2',
        '*** Update File: next.txt',
    ]
    section, chunks, idx, eof = peek_next_section(lines, 0)
    assert section == ['Del1', 'Keep1', 'Del2']
    assert len(chunks) == 2
    assert chunks[0].del_lines == ['Del1']
    assert chunks[0].ins_lines == ['Add1']
    assert chunks[0].orig_index == 0

    assert chunks[1].del_lines == ['Del2']
    assert chunks[1].ins_lines == ['Add2']
    assert chunks[1].orig_index == 2
    assert idx == 5
    assert not eof


def test_peek_next_section_eof():
    lines = [
        ' Line 1',
        '*** End of File',
    ]
    section, chunks, idx, eof = peek_next_section(lines, 0)
    assert section == ['Line 1']
    assert len(chunks) == 0  # No changes, only context
    assert idx == 2
    assert eof


def test_peek_next_section_empty_section():
    lines = ['@@ Next section']
    with pytest.raises(DiffError, match='Nothing in this section'):
        peek_next_section(lines, 0)


def test_peek_next_section_invalid_line_char():
    lines = ['xInvalid line']
    with pytest.raises(DiffError, match='Invalid Line: xInvalid line'):
        peek_next_section(lines, 0)


def test_peek_next_section_invalid_line_stars():
    lines = ['**** Invalid']
    with pytest.raises(DiffError, match=re.escape('Invalid Line: **** Invalid')):
        peek_next_section(lines, 0)


##
# Tests for _get_updated_file


def test_get_updated_file_simple():
    text = 'Line 1\nOld Line 2\nLine 3'
    action = PatchAction(type=ActionType.UPDATE, chunks=[
        Chunk(orig_index=1, del_lines=['Old Line 2'], ins_lines=['New Line 2']),
    ])
    updated = _get_updated_file(text, action, 'file.txt')
    assert updated == 'Line 1\nNew Line 2\nLine 3'


def test_get_updated_file_add_at_start():
    text = 'Line 1\nLine 2'
    action = PatchAction(type=ActionType.UPDATE, chunks=[
        Chunk(orig_index=0, del_lines=[], ins_lines=['New First Line']),
    ])
    updated = _get_updated_file(text, action, 'file.txt')
    assert updated == 'New First Line\nLine 1\nLine 2'


def test_get_updated_file_delete_at_end():
    text = 'Line 1\nLine 2\nLine 3'
    action = PatchAction(type=ActionType.UPDATE, chunks=[
        Chunk(orig_index=2, del_lines=['Line 3'], ins_lines=[]),
    ])
    updated = _get_updated_file(text, action, 'file.txt')
    assert updated == 'Line 1\nLine 2'


def test_get_updated_file_multiple_chunks():
    text = 'one\ntwo\nthree\nfour\nfive'
    action = PatchAction(type=ActionType.UPDATE, chunks=[
        Chunk(orig_index=1, del_lines=['two'], ins_lines=['2']),  # one\n2\nthree...
        Chunk(orig_index=3, del_lines=['four'], ins_lines=['4']),  # orig_index refers to original lines
        # three is at index 2 in original, four at 3
    ])
    # Expected after first chunk application (conceptually): "one\n2\nthree\nfour\nfive"
    # Second chunk applies to this conceptual state, orig_index 3 (original 'four')
    updated = _get_updated_file(text, action, 'file.txt')
    assert updated == 'one\n2\nthree\n4\nfive'


def test_get_updated_file_non_update_action():
    with pytest.raises(DiffError, match=re.escape('_get_updated_file called with non-update action')):
        _get_updated_file('', PatchAction(type=ActionType.ADD), 'file.txt')


def test_get_updated_file_orig_index_out_of_bounds():
    action = PatchAction(type=ActionType.UPDATE, chunks=[Chunk(orig_index=10)])
    with pytest.raises(DiffError, match=re.escape('file.txt: chunk.orig_index 10 exceeds file length')):
        _get_updated_file('hello', action, 'file.txt')


def test_get_updated_file_overlapping_chunks():
    text = 'Line 1\nLine 2\nLine 3\nLine 4'
    action = PatchAction(type=ActionType.UPDATE, chunks=[
        Chunk(orig_index=1, del_lines=['Line 2'], ins_lines=['L2']),
        Chunk(orig_index=0, del_lines=['Line 1'], ins_lines=['L1']),  # This chunk's index is before previous
    ])
    # Note: The check is `orig_index > chunk.orig_index` (previous > current), so it catches out-of-order chunks. For
    # true overlaps based on content changes, it's more complex. This tests the simple index order.
    with pytest.raises(DiffError):
        _get_updated_file(text, action, 'file.txt')


##
# Tests for patch_to_commit


def test_patch_to_commit_add():
    patch = Patch(actions={'new.txt': PatchAction(type=ActionType.ADD, new_file='content')})
    commit = patch_to_commit(patch, {})
    assert 'new.txt' in commit.changes
    change = commit.changes['new.txt']
    assert change.type == ActionType.ADD
    assert change.new_content == 'content'


def test_patch_to_commit_delete():
    orig = {'old.txt': 'content'}
    patch = Patch(actions={'old.txt': PatchAction(type=ActionType.DELETE)})
    commit = patch_to_commit(patch, orig)
    assert 'old.txt' in commit.changes
    change = commit.changes['old.txt']
    assert change.type == ActionType.DELETE
    assert change.old_content == 'content'


def test_patch_to_commit_add_no_content():
    patch = Patch(actions={'new.txt': PatchAction(type=ActionType.ADD, new_file=None)})
    with pytest.raises(DiffError, match='ADD action without file content'):
        patch_to_commit(patch, {})


##
# Tests for User-facing helpers


def test_text_to_patch_valid():
    patch_text_str = '*** Begin Patch\n*** Add File: a.txt\n+content\n*** End Patch'
    patch, fuzz = text_to_patch(patch_text_str, {})
    assert 'a.txt' in patch.actions
    assert fuzz == 0  # Assuming no fuzz in this simple case


def test_text_to_patch_invalid_sentinels_missing_begin():
    patch_text_str = '*** Add File: a.txt\n+content\n*** End Patch'
    with pytest.raises(DiffError, match='Invalid patch text - missing sentinels'):
        text_to_patch(patch_text_str, {})


def test_text_to_patch_invalid_sentinels_missing_end():
    patch_text_str = '*** Begin Patch\n*** Add File: a.txt\n+content'
    with pytest.raises(DiffError, match='Invalid patch text - missing sentinels'):
        text_to_patch(patch_text_str, {})


def test_identify_files_needed():
    text = textwrap.dedent("""\
    *** Update File: update1.txt
    *** Delete File: delete1.txt
    *** Add File: add1.txt
    *** Update File: update2.txt
    """)
    needed = identify_files_needed(text)
    assert sorted(needed) == sorted(['update1.txt', 'delete1.txt', 'update2.txt'])


def test_identify_files_added():
    text = textwrap.dedent("""\
    *** Update File: update1.txt
    *** Add File: add1.txt
    *** Add File: add2.txt
    """)
    added = identify_files_added(text)
    assert sorted(added) == sorted(['add1.txt', 'add2.txt'])
