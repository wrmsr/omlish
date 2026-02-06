# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import dataclasses as dc
import enum
import typing as ta

from omlish.lite.check import check

from .errors import EofYamlError
from .errors import YamlError
from .errors import YamlErrorOr
from .errors import yaml_error
from .tokens import YAML_RESERVED_TAG_KEYWORD_MAP
from .tokens import YamlIndicator
from .tokens import YamlPosition
from .tokens import YamlToken
from .tokens import YamlTokenMakers
from .tokens import YamlTokens
from .tokens import YamlTokenType
from .tokens import new_yaml_token


##


@dc.dataclass()
class InvalidTokenYamlError(YamlError):
    token: YamlToken

    @property
    def message(self) -> str:
        return check.not_none(self.token.error).message


def err_invalid_token(tk: YamlToken) -> InvalidTokenYamlError:
    return InvalidTokenYamlError(
        token=tk,
    )


##


# Context at scanning
@dc.dataclass()
class YamlScanningContext:
    idx: int = 0
    size: int = 0
    not_space_char_pos: int = 0
    not_space_org_char_pos: int = 0
    src: str = ''
    buf: str = ''
    obuf: str = ''
    tokens: YamlTokens = dc.field(default_factory=YamlTokens)
    mstate: ta.Optional['YamlMultiLineState'] = None

    def clear(self) -> None:
        self.reset_buffer()
        self.mstate = None

    def reset(self, src: str) -> None:
        self.idx = 0
        self.size = len(src)
        self.src = src
        self.tokens = YamlTokens()
        self.reset_buffer()
        self.mstate = None

    def reset_buffer(self) -> None:
        self.buf = ''
        self.obuf = ''
        self.not_space_char_pos = 0
        self.not_space_org_char_pos = 0

    def break_multi_line(self) -> None:
        self.mstate = None

    def get_multi_line_state(self) -> ta.Optional['YamlMultiLineState']:
        return self.mstate

    def set_literal(self, last_delim_column: int, opt: str) -> None:
        mstate = YamlMultiLineState(
            is_literal=True,
            opt=opt,
        )
        indent = first_line_indent_column_by_opt(opt)
        if indent > 0:
            mstate.first_line_indent_column = last_delim_column + indent
        self.mstate = mstate

    def set_folded(self, last_delim_column: int, opt: str) -> None:
        mstate = YamlMultiLineState(
            is_folded=True,
            opt=opt,
        )
        indent = first_line_indent_column_by_opt(opt)
        if indent > 0:
            mstate.first_line_indent_column = last_delim_column + indent
        self.mstate = mstate

    def set_raw_folded(self, column: int) -> None:
        mstate = YamlMultiLineState(
            is_raw_folded=True,
        )
        mstate.update_indent_column(column)
        self.mstate = mstate

    def add_token(self, tk: ta.Optional[YamlToken]) -> None:
        if tk is None:
            return
        self.tokens.append(tk)  # FIXME: .add??

    def add_buf(self, r: str) -> None:
        if len(self.buf) == 0 and (r == ' ' or r == '\t'):
            return
        self.buf += r
        if r != ' ' and r != '\t':
            self.not_space_char_pos = len(self.buf)

    def add_buf_with_tab(self, r: str) -> None:
        if len(self.buf) == 0 and r == ' ':
            return
        self.buf += r
        if r != ' ':
            self.not_space_char_pos = len(self.buf)

    def add_origin_buf(self, r: str) -> None:
        self.obuf += r
        if r != ' ' and r != '\t':
            self.not_space_org_char_pos = len(self.obuf)

    def remove_right_space_from_buf(self) -> None:
        trimmed_buf = self.obuf[:self.not_space_org_char_pos]
        buflen = len(trimmed_buf)
        diff = len(self.obuf) - buflen
        if diff > 0:
            self.obuf = self.obuf[:buflen]
            self.buf = self.buffered_src()

    def is_eos(self) -> bool:
        return len(self.src) - 1 <= self.idx

    def is_next_eos(self) -> bool:
        return len(self.src) <= self.idx + 1

    def next(self) -> bool:
        return self.idx < self.size

    def source(self, s: int, e: int) -> str:
        return self.src[s:e]

    def previous_char(self) -> str:
        if self.idx > 0:
            return self.src[self.idx - 1]
        return ''

    def current_char(self) -> str:
        if self.size > self.idx:
            return self.src[self.idx]
        return ''

    def next_char(self) -> str:
        if self.size > self.idx + 1:
            return self.src[self.idx + 1]
        return ''

    def repeat_num(self, r: str) -> int:
        cnt = 0
        for i in range(self.idx, self.size):
            if self.src[i] == r:
                cnt += 1
            else:
                break
        return cnt

    def progress(self, num: int) -> None:
        self.idx += num

    def exists_buffer(self) -> bool:
        return len(self.buffered_src()) != 0

    def is_multi_line(self) -> bool:
        return self.mstate is not None

    def buffered_src(self) -> str:
        src = self.buf[:self.not_space_char_pos]

        if self.is_multi_line():
            mstate = check.not_none(self.get_multi_line_state())

            # remove end '\n' character and trailing empty lines.
            # https://yaml.org/spec/1.2.2/#8112-block-chomping-indicator
            if mstate.has_trim_all_end_newline_opt():
                # If the '-' flag is specified, all trailing newline characters will be removed.
                src = src.rstrip('\n')

            elif not mstate.has_keep_all_end_newline_opt():
                # Normally, all but one of the trailing newline characters are removed.
                new_line_char_count = 0
                for i in range(len(src) - 1, -1, -1):
                    if src[i] == '\n':
                        new_line_char_count += 1
                        continue
                    break

                removed_new_line_char_count = new_line_char_count - 1
                while removed_new_line_char_count > 0:
                    src = src.rstrip('\n')
                    removed_new_line_char_count -= 1

            # If the text ends with a space character, remove all of them.
            if mstate.has_trim_all_end_newline_opt():
                src = src.rstrip(' ')

            if src == '\n':
                # If the content consists only of a newline, it can be considered as the document ending without any
                # specified value, so it is treated as an empty string.
                src = ''

            if mstate.has_keep_all_end_newline_opt() and len(src) == 0:
                src = '\n'

        return src

    def buffered_token(self, pos: YamlPosition) -> ta.Optional[YamlToken]:
        if self.idx == 0:
            return None

        source = self.buffered_src()
        if len(source) == 0:
            self.buf = self.buf[:0]  # clear value's buffer only.
            return None

        tk: ta.Optional[YamlToken]
        if self.is_multi_line():
            tk = YamlTokenMakers.new_string(source, self.obuf, pos)
        else:
            tk = new_yaml_token(source, self.obuf, pos)

        self.set_token_type_by_prev_tag(tk)
        self.reset_buffer()
        return tk

    def set_token_type_by_prev_tag(self, tk: ta.Optional[YamlToken]) -> None:
        last_tk = self.last_token()
        if last_tk is None:
            return

        if last_tk.type != YamlTokenType.TAG:
            return

        tag = last_tk.value
        if tag not in YAML_RESERVED_TAG_KEYWORD_MAP:
            check.not_none(tk).type = YamlTokenType.STRING

    def last_token(self) -> ta.Optional[YamlToken]:
        if len(self.tokens) != 0:
            return self.tokens[len(self.tokens) - 1]

        return None

    @staticmethod
    def new(src: str) -> 'YamlScanningContext':
        ctx = YamlScanningContext()
        ctx.reset(src)
        return ctx


##


@dc.dataclass()
class YamlMultiLineState:
    opt: str = ''
    first_line_indent_column: int = 0
    prev_line_indent_column: int = 0
    line_indent_column: int = 0
    last_not_space_only_line_indent_column: int = 0
    space_only_indent_column: int = 0
    folded_new_line: bool = False
    is_raw_folded: bool = False
    is_literal: bool = False
    is_folded: bool = False

    def last_delim_column(self) -> int:
        if self.first_line_indent_column == 0:
            return 0
        return self.first_line_indent_column - 1

    def update_indent_column(self, column: int) -> None:
        if self.first_line_indent_column == 0:
            self.first_line_indent_column = column
        if self.line_indent_column == 0:
            self.line_indent_column = column

    def update_space_only_indent_column(self, column: int) -> None:
        if self.first_line_indent_column != 0:
            return
        self.space_only_indent_column = column

    def validate_indent_after_space_only(self, column: int) -> ta.Optional[YamlError]:
        if self.first_line_indent_column != 0:
            return None
        if self.space_only_indent_column > column:
            return yaml_error('invalid number of indent is specified after space only')
        return None

    def validate_indent_column(self) -> ta.Optional[YamlError]:
        if first_line_indent_column_by_opt(self.opt) == 0:
            return None
        if self.first_line_indent_column > self.line_indent_column:
            return yaml_error('invalid number of indent is specified in the multi-line header')
        return None

    def update_new_line_state(self) -> None:
        self.prev_line_indent_column = self.line_indent_column
        if self.line_indent_column != 0:
            self.last_not_space_only_line_indent_column = self.line_indent_column
        self.folded_new_line = True
        self.line_indent_column = 0

    def is_indent_column(self, column: int) -> bool:
        if self.first_line_indent_column == 0:
            return column == 1
        return self.first_line_indent_column > column

    def add_indent(self, ctx: YamlScanningContext, column: int) -> None:
        if self.first_line_indent_column == 0:
            return

        # If the first line of the document has already been evaluated, the number is treated as the threshold, since
        # the `first_line_indent_column` is a positive number.
        if column < self.first_line_indent_column:
            return

        # `c.folded_new_line` is a variable that is set to True for every newline.
        if not self.is_literal and self.folded_new_line:
            self.folded_new_line = False

        # Since add_buf ignore space character, add to the buffer directly.
        ctx.buf += ' '
        ctx.not_space_char_pos = len(ctx.buf)

    # update_new_line_in_folded if Folded or RawFolded context and the content on the current line starts at the same
    # column as the previous line, treat the new-line-char as a space.
    def update_new_line_in_folded(self, ctx: YamlScanningContext, column: int) -> None:
        if self.is_literal:
            return

        # Folded or RawFolded.

        if not self.folded_new_line:
            return

        last_char = ''
        prev_last_char = ''
        if len(ctx.buf) != 0:
            last_char = ctx.buf[len(ctx.buf) - 1]
        if len(ctx.buf) > 1:
            prev_last_char = ctx.buf[len(ctx.buf) - 2]

        if self.line_indent_column == self.prev_line_indent_column:
            # ---
            # >
            #  a
            #  b
            if last_char == '\n':
                ctx.buf = ctx.buf[:-1] + ' '

        elif self.prev_line_indent_column == 0 and self.last_not_space_only_line_indent_column == column:
            # if previous line is indent-space and new-line-char only, prev_line_indent_column is zero. In this case,
            # last new-line-char is removed.
            # ---
            # >
            #  a
            #
            #  b
            if last_char == '\n' and prev_last_char == '\n':
                ctx.buf = ctx.buf[:len(ctx.buf) - 1]
                ctx.not_space_char_pos = len(ctx.buf)

        self.folded_new_line = False

    def has_trim_all_end_newline_opt(self) -> bool:
        return self.opt.startswith('-') or self.opt.endswith('-') or self.is_raw_folded

    def has_keep_all_end_newline_opt(self) -> bool:
        return self.opt.startswith('+') or self.opt.endswith('+')


##


def first_line_indent_column_by_opt(opt: str) -> int:
    opt = opt.lstrip('-')
    opt = opt.lstrip('+')
    opt = opt.rstrip('-')
    opt = opt.rstrip('+')
    try:
        return int(opt, 10)
    except ValueError:
        return 0


##


class YamlIndentState(enum.Enum):
    # EQUAL equals previous indent
    EQUAL = enum.auto()
    # UP more indent than previous
    UP = enum.auto()
    # DOWN less indent than previous
    DOWN = enum.auto()
    # KEEP uses not indent token
    KEEP = enum.auto()


# Scanner holds the scanner's internal state while processing a given text. It can be allocated as part of another data
# structure but must be initialized via init before use.
@dc.dataclass()
class YamlScanner:
    source: str = ''
    source_pos: int = 0
    source_size: int = 0
    # line number. This number starts from 1.
    line: int = 0
    # column number. This number starts from 1.
    column: int = 0
    # offset represents the offset from the beginning of the source.
    offset: int = 0
    # last_delim_column is the last column needed to compare indent is retained.
    last_delim_column: int = 0
    # indent_num indicates the number of spaces used for indentation.
    indent_num: int = 0
    # prev_line_indent_num indicates the number of spaces used for indentation at previous line.
    prev_line_indent_num: int = 0
    # indent_level indicates the level of indent depth. This value does not match the column value.
    indent_level: int = 0
    is_first_char_at_line: bool = False
    is_anchor: bool = False
    is_alias: bool = False
    is_directive: bool = False
    started_flow_sequence_num: int = 0
    started_flow_map_num: int = 0
    indent_state: YamlIndentState = YamlIndentState.EQUAL
    saved_pos: ta.Optional[YamlPosition] = None

    def pos(self) -> YamlPosition:
        return YamlPosition(
            line=self.line,
            column=self.column,
            offset=self.offset,
            indent_num=self.indent_num,
            indent_level=self.indent_level,
        )

    def buffered_token(self, ctx: YamlScanningContext) -> ta.Optional[YamlToken]:
        if self.saved_pos is not None:
            tk = ctx.buffered_token(self.saved_pos)
            self.saved_pos = None
            return tk

        line = self.line
        column = self.column - len(ctx.buf)
        level = self.indent_level
        if ctx.is_multi_line():
            line -= self.new_line_count(ctx.buf)
            column = ctx.obuf.find(ctx.buf) + 1
            # Since we are in a literal, folded or raw folded we can use the indent level from the last token.
            last = ctx.last_token()
            if last is not None:  # The last token should never be None here.
                level = last.position.indent_level + 1

        return ctx.buffered_token(YamlPosition(
            line=line,
            column=column,
            offset=self.offset - len(ctx.buf),
            indent_num=self.indent_num,
            indent_level=level,
        ))

    def progress_column(self, ctx: YamlScanningContext, num: int) -> None:
        self.column += num
        self.offset += num
        self.progress(ctx, num)

    def progress_only(self, ctx: YamlScanningContext, num: int) -> None:
        self.offset += num
        self.progress(ctx, num)

    def progress_line(self, ctx: YamlScanningContext) -> None:
        self.prev_line_indent_num = self.indent_num
        self.column = 1
        self.line += 1
        self.offset += 1
        self.indent_num = 0
        self.is_first_char_at_line = True
        self.is_anchor = False
        self.is_alias = False
        self.is_directive = False
        self.progress(ctx, 1)

    def progress(self, ctx: YamlScanningContext, num: int) -> None:
        ctx.progress(num)
        self.source_pos += num

    def is_new_line_char(self, c: str) -> bool:
        if c == '\n':
            return True
        if c == '\r':
            return True
        return False

    def new_line_count(self, src: str) -> int:
        size = len(src)
        cnt = 0
        i = -1
        while True:
            i += 1
            if not (i < size):
                break
            c = src[i]
            if c == '\r':
                if i + 1 < size and src[i + 1] == '\n':
                    i += 1
                cnt += 1
            elif c == '\n':
                cnt += 1
        return cnt

    def update_indent_level(self) -> None:
        if self.prev_line_indent_num < self.indent_num:
            self.indent_level += 1
        elif self.prev_line_indent_num > self.indent_num:
            if self.indent_level > 0:
                self.indent_level -= 1

    def update_indent_state(self, ctx: YamlScanningContext) -> None:
        if self.last_delim_column == 0:
            return

        if self.last_delim_column < self.column:
            self.indent_state = YamlIndentState.UP
        else:
            # If last_delim_column and self.column are the same, treat as Down state since it is the same column as
            # delimiter.
            self.indent_state = YamlIndentState.DOWN

    def update_indent(self, ctx: YamlScanningContext, c: str) -> None:
        if self.is_first_char_at_line and self.is_new_line_char(c):
            return
        if self.is_first_char_at_line and c == ' ':
            self.indent_num += 1
            return
        if self.is_first_char_at_line and c == '\t':
            # Found tab indent. In this case, scan_tab returns error.
            return
        if not self.is_first_char_at_line:
            self.indent_state = YamlIndentState.KEEP
            return
        self.update_indent_level()
        self.update_indent_state(ctx)
        self.is_first_char_at_line = False

    def is_changed_to_indent_state_down(self) -> bool:
        return self.indent_state == YamlIndentState.DOWN

    def is_changed_to_indent_state_up(self) -> bool:
        return self.indent_state == YamlIndentState.UP

    def add_buffered_token_if_exists(self, ctx: YamlScanningContext) -> None:
        ctx.add_token(self.buffered_token(ctx))

    def break_multi_line(self, ctx: YamlScanningContext) -> None:
        ctx.break_multi_line()

    def scan_single_quote(self, ctx: YamlScanningContext) -> YamlErrorOr[YamlToken]:
        ctx.add_origin_buf("'")
        srcpos = self.pos()
        start_index = ctx.idx + 1
        src = ctx.src
        size = len(src)
        value = ''
        is_first_line_char = False
        is_new_line = False

        idx = start_index - 1
        while True:
            idx += 1
            if not (idx < size):
                break

            if not is_new_line:
                self.progress_column(ctx, 1)
            else:
                is_new_line = False

            c = src[idx]
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                not_space_idx = -1
                for i in range(len(value) - 1, -1, -1):
                    if value[i] == ' ':
                        continue
                    not_space_idx = i
                    break

                if len(value) > not_space_idx:
                    value = value[:not_space_idx + 1]
                if is_first_line_char:
                    value += '\n'
                else:
                    value += ' '

                is_first_line_char = True
                is_new_line = True
                self.progress_line(ctx)
                if idx + 1 < size:
                    if (err := self.validate_document_separator_marker(ctx, src[idx + 1:])) is not None:
                        return err

                continue

            if is_first_line_char and c == ' ':
                continue

            if is_first_line_char and c == '\t':
                if self.last_delim_column >= self.column:
                    return err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error('tab character cannot be used for indentation in single-quoted text'),
                            ctx.obuf,
                            self.pos(),
                        ),
                    )

                continue

            if c != "'":
                value += c
                is_first_line_char = False
                continue

            if idx + 1 < len(ctx.src) and ctx.src[idx + 1] == '\'':
                # '' handle as ' character
                value += c
                ctx.add_origin_buf(c)
                idx += 1
                self.progress_column(ctx, 1)
                continue

            self.progress_column(ctx, 1)
            return YamlTokenMakers.new_single_quote(value, ctx.obuf, srcpos)

        self.progress_column(ctx, 1)
        return err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error('could not find end character of single-quoted text'),
                ctx.obuf,
                srcpos,
            ),
        )

    def scan_double_quote(self, ctx: YamlScanningContext) -> YamlErrorOr[YamlToken]:
        ctx.add_origin_buf('"')
        srcpos = self.pos()
        start_index = ctx.idx + 1
        src = ctx.src
        size = len(src)
        value = ''
        is_first_line_char = False
        is_new_line = False

        idx = start_index - 1
        while True:
            idx += 1
            if not (idx < size):
                break

            if not is_new_line:
                self.progress_column(ctx, 1)
            else:
                is_new_line = False

            c = src[idx]
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                not_space_idx = -1
                for i in range(len(value) - 1, -1, -1):
                    if value[i] == ' ':
                        continue
                    not_space_idx = i
                    break

                if len(value) > not_space_idx:
                    value = value[:not_space_idx + 1]

                if is_first_line_char:
                    value += '\n'
                else:
                    value += ' '

                is_first_line_char = True
                is_new_line = True
                self.progress_line(ctx)
                if idx + 1 < size:
                    if (err := self.validate_document_separator_marker(ctx, src[idx + 1:])) is not None:
                        return err

                continue

            if is_first_line_char and c == ' ':
                continue

            if is_first_line_char and c == '\t':
                if self.last_delim_column >= self.column:
                    return err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error('tab character cannot be used for indentation in double-quoted text'),
                            ctx.obuf,
                            self.pos(),
                        ),
                    )

                continue

            if c == '\\':
                is_first_line_char = False
                if idx + 1 >= size:
                    value += c
                    continue

                next_char = src[idx + 1]
                progress = 0

                if next_char == '0':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += chr(0)
                elif next_char == 'a':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x07'
                elif next_char == 'b':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x08'
                elif next_char == 't':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x09'
                elif next_char == 'n':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0A'
                elif next_char == 'v':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0B'
                elif next_char == 'f':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0C'
                elif next_char == 'r':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0D'
                elif next_char == 'e':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x1B'
                elif next_char == ' ':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x20'
                elif next_char == '"':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x22'
                elif next_char == '/':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x2F'
                elif next_char == '\\':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x5C'
                elif next_char == 'N':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x85'
                elif next_char == '_':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\xA0'
                elif next_char == 'L':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\u2028'
                elif next_char == 'P':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\u2029'

                elif next_char == 'x':
                    if idx + 3 >= size:
                        progress = 1
                        ctx.add_origin_buf(next_char)
                        value += next_char
                    else:
                        progress = 3
                        code_num = hex_runes_to_int(src[idx + 2: idx + progress + 1])
                        value += chr(code_num)

                elif next_char == 'u':
                    # \u0000 style must have 5 characters at least.
                    if idx + 5 >= size:
                        return err_invalid_token(
                            YamlTokenMakers.new_invalid(
                                yaml_error('not enough length for escaped UTF-16 character'),
                                ctx.obuf,
                                self.pos(),
                            ),
                        )

                    progress = 5
                    code_num = hex_runes_to_int(src[idx + 2: idx + 6])

                    # handle surrogate pairs.
                    if code_num >= 0xD800 and code_num <= 0xDBFF:
                        high = code_num

                        # \u0000\u0000 style must have 11 characters at least.
                        if idx + 11 >= size:
                            return err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('not enough length for escaped UTF-16 surrogate pair'),
                                    ctx.obuf,
                                    self.pos(),
                                ),
                            )

                        if src[idx + 6] != '\\' or src[idx + 7] != 'u':
                            return err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('found unexpected character after high surrogate for UTF-16 surrogate pair'),  # noqa
                                    ctx.obuf,
                                    self.pos(),
                                ),
                            )

                        low = hex_runes_to_int(src[idx + 8: idx + 12])
                        if low < 0xDC00 or low > 0xDFFF:
                            return err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('found unexpected low surrogate after high surrogate'),
                                    ctx.obuf,
                                    self.pos(),
                                ),
                            )

                        code_num = ((high - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000
                        progress += 6

                    value += chr(code_num)

                elif next_char == 'U':
                    # \U00000000 style must have 9 characters at least.
                    if idx + 9 >= size:
                        return err_invalid_token(
                            YamlTokenMakers.new_invalid(
                                yaml_error('not enough length for escaped UTF-32 character'),
                                ctx.obuf,
                                self.pos(),
                            ),
                        )

                    progress = 9
                    code_num = hex_runes_to_int(src[idx + 2: idx + 10])
                    value += chr(code_num)

                elif next_char == '\n':
                    is_first_line_char = True
                    is_new_line = True
                    ctx.add_origin_buf(next_char)
                    self.progress_column(ctx, 1)
                    self.progress_line(ctx)
                    idx += 1
                    continue

                elif next_char == '\r':
                    is_first_line_char = True
                    is_new_line = True
                    ctx.add_origin_buf(next_char)
                    self.progress_line(ctx)
                    progress = 1
                    # Skip \n after \r in CRLF sequences
                    if idx + 2 < size and src[idx + 2] == '\n':
                        ctx.add_origin_buf('\n')
                        progress = 2

                elif next_char == '\t':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += next_char

                else:
                    self.progress_column(ctx, 1)
                    return err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error(f'found unknown escape character {next_char!r}'),
                            ctx.obuf,
                            self.pos(),
                        ),
                    )

                idx += progress
                self.progress_column(ctx, progress)
                continue

            if c == '\t':
                found_not_space_char = False
                progress = 0

                for i in range(idx + 1, size):
                    if src[i] == ' ' or src[i] == '\t':
                        progress += 1
                        continue

                    if self.is_new_line_char(src[i]):
                        break

                    found_not_space_char = True

                if found_not_space_char:
                    value += c
                    if src[idx + 1] != '"':
                        self.progress_column(ctx, 1)

                else:
                    idx += progress
                    self.progress_column(ctx, progress)

                continue

            if c != '"':
                value += c
                is_first_line_char = False
                continue

            self.progress_column(ctx, 1)
            return YamlTokenMakers.new_double_quote(value, ctx.obuf, srcpos)

        self.progress_column(ctx, 1)
        return err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error('could not find end character of double-quoted text'),
                ctx.obuf,
                srcpos,
            ),
        )

    def validate_document_separator_marker(self, ctx: YamlScanningContext, src: str) -> ta.Optional[YamlError]:
        if self.found_document_separator_marker(src):
            return err_invalid_token(
                YamlTokenMakers.new_invalid(yaml_error('found unexpected document separator'), ctx.obuf, self.pos()),
            )

        return None

    def found_document_separator_marker(self, src: str) -> bool:
        if len(src) < 3:
            return False

        marker = ''
        if len(src) == 3:
            marker = src
        else:
            marker = trim_right_func(src[:4], lambda r: r == ' ' or r == '\t' or r == '\n' or r == '\r')

        return marker == '---' or marker == '...'

    def scan_quote(self, ctx: YamlScanningContext, ch: str) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        if ch == "'":
            tk = self.scan_single_quote(ctx)
            if isinstance(tk, YamlError):
                return tk

            ctx.add_token(tk)

        else:
            tk = self.scan_double_quote(ctx)
            if isinstance(tk, YamlError):
                return tk

            ctx.add_token(tk)

        ctx.clear()
        return True

    def scan_white_space(self, ctx: YamlScanningContext) -> bool:
        if ctx.is_multi_line():
            return False

        if not self.is_anchor and not self.is_directive and not self.is_alias and not self.is_first_char_at_line:
            return False

        if self.is_first_char_at_line:
            self.progress_column(ctx, 1)
            ctx.add_origin_buf(' ')
            return True

        if self.is_directive:
            self.add_buffered_token_if_exists(ctx)
            self.progress_column(ctx, 1)
            ctx.add_origin_buf(' ')
            return True

        self.add_buffered_token_if_exists(ctx)
        self.is_anchor = False
        self.is_alias = False
        return True

    def is_merge_key(self, ctx: YamlScanningContext) -> bool:
        if ctx.repeat_num('<') != 2:
            return False

        src = ctx.src
        size = len(src)
        for idx in range(ctx.idx + 2, size):
            c = src[idx]
            if c == ' ':
                continue

            if c != ':':
                return False

            if idx + 1 < size:
                nc = src[idx + 1]
                if nc == ' ' or self.is_new_line_char(nc):
                    return True

        return False

    def scan_tag(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer() or self.is_directive:
            return False

        ctx.add_origin_buf('!')
        self.progress(ctx, 1)  # skip '!' character

        progress = 0
        for idx, c in enumerate(ctx.src[ctx.idx:]):
            progress = idx + 1

            if c == ' ':
                ctx.add_origin_buf(c)
                value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                ctx.add_token(YamlTokenMakers.new_tag(value, ctx.obuf, self.pos()))
                self.progress_column(ctx, len(value))
                ctx.clear()
                return True

            elif c == ',':
                if self.started_flow_sequence_num > 0 or self.started_flow_map_num > 0:
                    value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                    ctx.add_token(YamlTokenMakers.new_tag(value, ctx.obuf, self.pos()))
                    # progress column before collect-entry for scanning it at scan_flow_entry function.
                    self.progress_column(ctx, len(value) - 1)
                    ctx.clear()
                    return True
                else:
                    ctx.add_origin_buf(c)

            elif c in ('\n', '\r'):
                ctx.add_origin_buf(c)
                value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                ctx.add_token(YamlTokenMakers.new_tag(value, ctx.obuf, self.pos()))
                # progress column before new-line-char for scanning new-line-char at scan_new_line function.
                self.progress_column(ctx, len(value) - 1)
                ctx.clear()
                return True

            elif c in ('{', '}'):
                ctx.add_origin_buf(c)
                self.progress_column(ctx, progress)
                invalid_tk = YamlTokenMakers.new_invalid(
                    yaml_error(f'found invalid tag character {c!r}'),
                    ctx.obuf,
                    self.pos(),
                )
                return err_invalid_token(invalid_tk)

            else:
                ctx.add_origin_buf(c)

        self.progress_column(ctx, progress)
        ctx.clear()
        return True

    def scan_comment(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            c = ctx.previous_char()
            if c != ' ' and c != '\t' and not self.is_new_line_char(c):
                return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('#')
        self.progress(ctx, 1)  # skip '#' character

        for idx, c in enumerate(ctx.src[ctx.idx:]):
            ctx.add_origin_buf(c)
            if not self.is_new_line_char(c):
                continue
            if ctx.previous_char() == '\\':
                continue

            value = ctx.source(ctx.idx, ctx.idx + idx)
            progress = len(value)
            ctx.add_token(YamlTokenMakers.new_comment(value, ctx.obuf, self.pos()))
            self.progress_column(ctx, progress)
            self.progress_line(ctx)
            ctx.clear()
            return True

        # document ends with comment.
        value = ctx.src[ctx.idx:]
        ctx.add_token(YamlTokenMakers.new_comment(value, ctx.obuf, self.pos()))
        progress = len(value)
        self.progress_column(ctx, progress)
        self.progress_line(ctx)
        ctx.clear()
        return True

    def scan_multi_line(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        state = check.not_none(ctx.get_multi_line_state())
        ctx.add_origin_buf(c)

        if ctx.is_eos():
            if self.is_first_char_at_line and c == ' ':
                state.add_indent(ctx, self.column)
            else:
                ctx.add_buf(c)

            state.update_indent_column(self.column)
            if (err := state.validate_indent_column()) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ctx.obuf, self.pos())
                self.progress_column(ctx, 1)
                return err_invalid_token(invalid_tk)

            value = ctx.buffered_src()
            ctx.add_token(YamlTokenMakers.new_string(value, ctx.obuf, self.pos()))
            ctx.clear()
            self.progress_column(ctx, 1)

        elif self.is_new_line_char(c):
            ctx.add_buf(c)
            state.update_space_only_indent_column(self.column - 1)
            state.update_new_line_state()
            self.progress_line(ctx)
            if ctx.next():
                if self.found_document_separator_marker(ctx.src[ctx.idx:]):
                    value = ctx.buffered_src()
                    ctx.add_token(YamlTokenMakers.new_string(value, ctx.obuf, self.pos()))
                    ctx.clear()
                    self.break_multi_line(ctx)

        elif self.is_first_char_at_line and c == ' ':
            state.add_indent(ctx, self.column)
            self.progress_column(ctx, 1)

        elif self.is_first_char_at_line and c == '\t' and state.is_indent_column(self.column):
            err = err_invalid_token(
                YamlTokenMakers.new_invalid(
                    yaml_error('found a tab character where an indentation space is expected'),
                    ctx.obuf,
                    self.pos(),
                ),
            )
            self.progress_column(ctx, 1)
            return err

        elif c == '\t' and not state.is_indent_column(self.column):
            ctx.add_buf_with_tab(c)
            self.progress_column(ctx, 1)

        else:
            if (err := state.validate_indent_after_space_only(self.column)) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ctx.obuf, self.pos())
                self.progress_column(ctx, 1)
                return err_invalid_token(invalid_tk)

            state.update_indent_column(self.column)
            if (err := state.validate_indent_column()) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ctx.obuf, self.pos())
                self.progress_column(ctx, 1)
                return err_invalid_token(invalid_tk)

            if (col := state.last_delim_column()) > 0:
                self.last_delim_column = col

            state.update_new_line_in_folded(ctx, self.column)
            ctx.add_buf_with_tab(c)
            self.progress_column(ctx, 1)

        return None

    def scan_new_line(self, ctx: YamlScanningContext, c: str) -> None:
        if len(ctx.buf) > 0 and self.saved_pos is None:
            buf_len = len(ctx.buffered_src())
            self.saved_pos = self.pos()
            self.saved_pos.column -= buf_len
            self.saved_pos.offset -= buf_len

        # if the following case, origin buffer has unnecessary two spaces.
        # So, `removeRightSpaceFromOriginBuf` remove them, also fix column number too.
        # ---
        # a:[space][space]
        #   b: c
        ctx.remove_right_space_from_buf()

        # There is no problem that we ignore CR which followed by LF and normalize it to LF, because of following
        # YAML1.2 spec.
        # > Line breaks inside scalar content must be normalized by the YAML processor. Each such line break must be
        #   parsed into a single line feed character.
        # > Outside scalar content, YAML allows any line break to be used to terminate lines.
        # > -- https://yaml.org/spec/1.2/spec.html
        if c == '\r' and ctx.next_char() == '\n':
            ctx.add_origin_buf('\r')
            self.progress(ctx, 1)
            self.offset += 1
            c = '\n'

        if ctx.is_eos():
            self.add_buffered_token_if_exists(ctx)
        elif self.is_anchor or self.is_alias or self.is_directive:
            self.add_buffered_token_if_exists(ctx)

        if ctx.exists_buffer() and self.is_first_char_at_line:
            if ctx.buf[len(ctx.buf) - 1] == ' ':
                ctx.buf = ctx.buf[:-1] + '\n'
            else:
                ctx.buf += '\n'
        else:
            ctx.add_buf(' ')

        ctx.add_origin_buf(c)
        self.progress_line(ctx)

    def is_flow_mode(self) -> bool:
        if self.started_flow_sequence_num > 0:
            return True

        if self.started_flow_map_num > 0:
            return True

        return False

    def scan_flow_map_start(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and not self.is_flow_mode():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('{')
        ctx.add_token(YamlTokenMakers.new_mapping_start(ctx.obuf, self.pos()))
        self.started_flow_map_num += 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_map_end(self, ctx: YamlScanningContext) -> bool:
        if self.started_flow_map_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('}')
        ctx.add_token(YamlTokenMakers.new_mapping_end(ctx.obuf, self.pos()))
        self.started_flow_map_num -= 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_array_start(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and not self.is_flow_mode():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('[')
        ctx.add_token(YamlTokenMakers.new_sequence_start(ctx.obuf, self.pos()))
        self.started_flow_sequence_num += 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_array_end(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and self.started_flow_sequence_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf(']')
        ctx.add_token(YamlTokenMakers.new_sequence_end(ctx.obuf, self.pos()))
        self.started_flow_sequence_num -= 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_entry(self, ctx: YamlScanningContext, c: str) -> bool:
        if self.started_flow_sequence_num <= 0 and self.started_flow_map_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf(c)
        ctx.add_token(YamlTokenMakers.new_collect_entry(ctx.obuf, self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_map_delim(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        nc = ctx.next_char()
        if self.is_directive or self.is_anchor or self.is_alias:
            return False

        if (
                self.started_flow_map_num <= 0 and
                nc != ' ' and
                nc != '\t' and
                not self.is_new_line_char(nc) and
                not ctx.is_next_eos()
        ):
            return False

        if self.started_flow_map_num > 0 and nc == '/':
            # like http://
            return False

        if self.started_flow_map_num > 0:
            tk = ctx.last_token()
            if tk is not None and tk.type == YamlTokenType.MAPPING_VALUE:
                return False

        if ctx.obuf.lstrip(' ').startswith('\t') and not ctx.buf.startswith('\t'):
            invalid_tk = YamlTokenMakers.new_invalid(
                yaml_error('tab character cannot use as a map key directly'),
                ctx.obuf,
                self.pos(),
            )
            self.progress_column(ctx, 1)
            return err_invalid_token(invalid_tk)

        # mapping value
        tk = self.buffered_token(ctx)
        if tk is not None:
            self.last_delim_column = tk.position.column
            ctx.add_token(tk)

        elif (tk := ctx.last_token()) is not None:
            # If the map key is quote, the buffer does not exist because it has already been cut into tokens.
            # Therefore, we need to check the last token.
            if tk.indicator == YamlIndicator.QUOTED_SCALAR:
                self.last_delim_column = tk.position.column

        ctx.add_token(YamlTokenMakers.new_mapping_value(self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_document_start(self, ctx: YamlScanningContext) -> bool:
        if self.indent_num != 0:
            return False

        if self.column != 1:
            return False

        if ctx.repeat_num('-') != 3:
            return False

        if ctx.size > ctx.idx + 3:
            c = ctx.src[ctx.idx + 3]
            if c != ' ' and c != '\t' and c != '\n' and c != '\r':
                return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_token(YamlTokenMakers.new_document_header(ctx.obuf + '---', self.pos()))
        self.progress_column(ctx, 3)
        ctx.clear()
        self.clear_state()
        return True

    def scan_document_end(self, ctx: YamlScanningContext) -> bool:
        if self.indent_num != 0:
            return False

        if self.column != 1:
            return False

        if ctx.repeat_num('.') != 3:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_token(YamlTokenMakers.new_document_end(ctx.obuf + '...', self.pos()))
        self.progress_column(ctx, 3)
        ctx.clear()
        return True

    def scan_merge_key(self, ctx: YamlScanningContext) -> bool:
        if not self.is_merge_key(ctx):
            return False

        self.last_delim_column = self.column
        ctx.add_token(YamlTokenMakers.new_merge_key(ctx.obuf + '<<', self.pos()))
        self.progress_column(ctx, 2)
        ctx.clear()
        return True

    def scan_raw_folded_char(self, ctx: YamlScanningContext) -> bool:
        if not ctx.exists_buffer():
            return False

        if not self.is_changed_to_indent_state_up():
            return False

        ctx.set_raw_folded(self.column)
        ctx.add_buf('-')
        ctx.add_origin_buf('-')
        self.progress_column(ctx, 1)
        return True

    def scan_sequence(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        nc = ctx.next_char()
        if nc != 0 and nc != ' ' and nc != '\t' and not self.is_new_line_char(nc):
            return False

        if ctx.obuf.lstrip(' ').startswith('\t'):
            invalid_tk = YamlTokenMakers.new_invalid(
                yaml_error('tab character cannot use as a sequence delimiter'),
                ctx.obuf,
                self.pos(),
            )
            self.progress_column(ctx, 1)
            return err_invalid_token(invalid_tk)

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('-')
        tk = YamlTokenMakers.new_sequence_entry(ctx.obuf, self.pos())
        self.last_delim_column = tk.position.column
        ctx.add_token(tk)
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_multi_line_header(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        if (err := self.scan_multi_line_header_option(ctx)) is not None:
            return err

        self.progress_line(ctx)
        return True

    def validate_multi_line_header_option(self, opt: str) -> ta.Optional[YamlError]:
        if len(opt) == 0:
            return None

        org_opt = opt
        opt = opt.lstrip('-')
        opt = opt.lstrip('+')
        opt = opt.rstrip('-')
        opt = opt.rstrip('+')
        if len(opt) == 0:
            return None

        if opt == '0':
            return yaml_error(f'invalid header option: {org_opt!r}')

        try:
            i = int(opt, 10)
        except ValueError:
            return yaml_error(f'invalid header option: {org_opt!r}')

        if i > 9:
            return yaml_error(f'invalid header option: {org_opt!r}')

        return None

    def scan_multi_line_header_option(self, ctx: YamlScanningContext) -> ta.Optional[YamlError]:
        header = ctx.current_char()
        ctx.add_origin_buf(header)
        self.progress(ctx, 1)  # skip '|' or '>' character

        progress = 0
        for idx, c in enumerate(ctx.src[ctx.idx:]):
            progress = idx
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                break

        value = ctx.source(ctx.idx, ctx.idx + progress).rstrip(' ')
        comment_value_index = value.find('#')
        opt = value
        if comment_value_index > 0:
            opt = value[:comment_value_index]

        opt = trim_right_func(opt, lambda r: r == ' ' or r == '\t')

        if len(opt) != 0:
            if (err := self.validate_multi_line_header_option(opt)) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ctx.obuf, self.pos())
                self.progress_column(ctx, progress)
                return err_invalid_token(invalid_tk)

        if self.column == 1:
            self.last_delim_column = 1

        comment_index = ctx.obuf.find('#')
        header_buf = ctx.obuf
        if comment_index > 0:
            header_buf = header_buf[:comment_index]

        if header == '|':
            ctx.add_token(YamlTokenMakers.new_literal('|' + opt, header_buf, self.pos()))
            ctx.set_literal(self.last_delim_column, opt)
        elif header == '>':
            ctx.add_token(YamlTokenMakers.new_folded('>' + opt, header_buf, self.pos()))
            ctx.set_folded(self.last_delim_column, opt)

        if comment_index > 0:
            comment = value[comment_value_index + 1:]
            self.offset += len(header_buf)
            self.column += len(header_buf)
            ctx.add_token(YamlTokenMakers.new_comment(comment, ctx.obuf[len(header_buf):], self.pos()))

        self.indent_state = YamlIndentState.KEEP
        ctx.reset_buffer()
        self.progress_column(ctx, progress)
        return None

    def scan_map_key(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        nc = ctx.next_char()
        if nc != ' ' and nc != '\t':
            return False

        tk = YamlTokenMakers.new_mapping_key(self.pos())
        self.last_delim_column = tk.position.column
        ctx.add_token(tk)
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_directive(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False
        if self.indent_num != 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('%')
        ctx.add_token(YamlTokenMakers.new_directive(ctx.obuf, self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        self.is_directive = True
        return True

    def scan_anchor(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('&')
        ctx.add_token(YamlTokenMakers.new_anchor(ctx.obuf, self.pos()))
        self.progress_column(ctx, 1)
        self.is_anchor = True
        ctx.clear()
        return True

    def scan_alias(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('*')
        ctx.add_token(YamlTokenMakers.new_alias(ctx.obuf, self.pos()))
        self.progress_column(ctx, 1)
        self.is_alias = True
        ctx.clear()
        return True

    def scan_reserved_char(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        if ctx.exists_buffer():
            return None

        ctx.add_buf(c)
        ctx.add_origin_buf(c)
        err = err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error(f'{c!r} is a reserved character'),
                ctx.obuf,
                self.pos(),
            ),
        )
        self.progress_column(ctx, 1)
        ctx.clear()
        return err

    def scan_tab(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        if self.started_flow_sequence_num > 0 or self.started_flow_map_num > 0:
            # tabs character is allowed in flow mode.
            return None

        if not self.is_first_char_at_line:
            return None

        ctx.add_buf(c)
        ctx.add_origin_buf(c)
        err = err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error("found character '\t' that cannot start any token"),
                ctx.obuf,
                self.pos(),
            ),
        )
        self.progress_column(ctx, 1)
        ctx.clear()
        return err

    def _scan(self, ctx: YamlScanningContext) -> ta.Optional[YamlError]:
        while ctx.next():
            c = ctx.current_char()
            # First, change the IndentState.
            # If the target character is the first character in a line, IndentState is Up/Down/Equal state.
            # The second and subsequent letters are Keep.
            self.update_indent(ctx, c)

            # If IndentState is down, tokens are split, so the buffer accumulated until that point needs to be cutted as
            # a token.
            if self.is_changed_to_indent_state_down():
                self.add_buffered_token_if_exists(ctx)

            if ctx.is_multi_line():
                if self.is_changed_to_indent_state_down():
                    if (tk := ctx.last_token()) is not None:
                        # If literal/folded content is empty, no string token is added.
                        # Therefore, add an empty string token.
                        # But if literal/folded token column is 1, it is invalid at down state.
                        if tk.position.column == 1:
                            return yaml_error(err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('could not find multi-line content'),
                                    ctx.obuf,
                                    self.pos(),
                                ),
                            ))

                        if tk.type != YamlTokenType.STRING:
                            ctx.add_token(YamlTokenMakers.new_string('', '', self.pos()))

                    self.break_multi_line(ctx)

                else:
                    if (err := self.scan_multi_line(ctx, c)) is not None:
                        return err

                    continue

            if c == '{':
                if self.scan_flow_map_start(ctx):
                    continue

            elif c == '}':
                if self.scan_flow_map_end(ctx):
                    continue

            elif c == '.':
                if self.scan_document_end(ctx):
                    continue

            elif c == '<':
                if self.scan_merge_key(ctx):
                    continue

            elif c == '-':
                if self.scan_document_start(ctx):
                    continue

                if self.scan_raw_folded_char(ctx):
                    continue

                scanned = self.scan_sequence(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '[':
                if self.scan_flow_array_start(ctx):
                    continue

            elif c == ']':
                if self.scan_flow_array_end(ctx):
                    continue

            elif c == ',':
                if self.scan_flow_entry(ctx, c):
                    continue

            elif c == ':':
                scanned = self.scan_map_delim(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c in ('|', '>'):
                scanned = self.scan_multi_line_header(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '!':
                scanned = self.scan_tag(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '%':
                if self.scan_directive(ctx):
                    continue

            elif c == '?':
                if self.scan_map_key(ctx):
                    continue

            elif c == '&':
                if self.scan_anchor(ctx):
                    continue

            elif c == '*':
                if self.scan_alias(ctx):
                    continue

            elif c == '#':
                if self.scan_comment(ctx):
                    continue

            elif c in ("'", '"'):
                scanned = self.scan_quote(ctx, c)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c in ('\r', '\n'):
                self.scan_new_line(ctx, c)
                continue

            elif c == ' ':
                if self.scan_white_space(ctx):
                    continue

            elif c in ('@', '`'):
                if (err := self.scan_reserved_char(ctx, c)) is not None:
                    return err

            elif c == '\t':
                if ctx.exists_buffer() and self.last_delim_column == 0:
                    # tab indent for plain text (yaml-test-suite's spec-example-7-12-plain-lines).
                    self.indent_num += 1
                    ctx.add_origin_buf(c)
                    self.progress_only(ctx, 1)
                    continue

                if self.last_delim_column < self.column:
                    self.indent_num += 1
                    ctx.add_origin_buf(c)
                    self.progress_only(ctx, 1)
                    continue

                if (err := self.scan_tab(ctx, c)) is not None:
                    return err

            ctx.add_buf(c)
            ctx.add_origin_buf(c)
            self.progress_column(ctx, 1)

        self.add_buffered_token_if_exists(ctx)
        return None

    # init prepares the scanner s to tokenize the text src by setting the scanner at the beginning of src.
    def init(self, text: str) -> None:
        src = text
        self.source = src
        self.source_pos = 0
        self.source_size = len(src)
        self.line = 1
        self.column = 1
        self.offset = 1
        self.is_first_char_at_line = True
        self.clear_state()

    def clear_state(self) -> None:
        self.prev_line_indent_num = 0
        self.last_delim_column = 0
        self.indent_level = 0
        self.indent_num = 0

    # scan scans the next token and returns the token collection. The source end is indicated by io.EOF.
    def scan(self) -> ta.Tuple[ta.Optional[YamlTokens], ta.Optional[YamlError]]:
        if self.source_pos >= self.source_size:
            return None, EofYamlError()

        ctx = YamlScanningContext.new(self.source[self.source_pos:])

        lst = YamlTokens()
        err = self._scan(ctx)
        lst.extend(ctx.tokens)

        if err is not None:
            # var invalidTokenErr *InvalidTokenError
            # if errors.As(err, &invalidTokenErr):
            #     lst = append(lst, invalidTokenErr.Token)
            return lst, err

        return lst, None


# Tokenize split to token instances from string
def yaml_tokenize(src: str) -> YamlTokens:
    s = YamlScanner()
    s.init(src)

    tks = YamlTokens()
    while True:
        sub_tokens, err = s.scan()
        if isinstance(err, EofYamlError):
            break

        tks.add(*check.not_none(sub_tokens))

    return tks


##


def hex_to_int(s: str) -> int:
    if len(s) != 1:
        raise ValueError(s)
    b = s[0]
    if 'A' <= b <= 'F':
        return ord(b) - ord('A') + 10
    if 'a' <= b <= 'f':
        return ord(b) - ord('a') + 10
    return ord(b) - ord('0')


def hex_runes_to_int(b: str) -> int:
    n = 0
    for i in range(len(b)):
        n += hex_to_int(b[i]) << ((len(b) - i - 1) * 4)
    return n


def trim_right_func(s: str, predicate: ta.Callable[[str], bool]) -> str:
    if not s:
        return s

    i = len(s) - 1
    while i >= 0 and predicate(s[i]):
        i -= 1

    return s[:i + 1]
