from rich.align import AlignMethod
from rich.cells import cell_len
from rich.cells import set_cell_size
from rich.console import Console
from rich.console import ConsoleOptions
from rich.console import RenderResult
from rich.jupyter import JupyterMixin
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text

from omlish import check


##


class TriRule(JupyterMixin):
    """
    A console renderable to draw a horizontal rule (line).

    Args:
        title (str | Text, optional): Text to render in the rule. Defaults to "".
        left (str | Text, optional): Text to render at the left edge.
        center (str | Text, optional): Text to render centered.
        right (str | Text, optional): Text to render at the right edge.
        characters (str, optional): Character(s) used to draw the line. Defaults to "─".
        style (StyleType, optional): Style of TriRule. Defaults to "rule.line".
        end (str, optional): Character at end of TriRule. defaults to "\\n"
        align (str, optional): Where legacy `title` goes if explicit slot not provided.
        min_left_length (int | None): Best-effort minimum visible cell width for left text.
        min_right_length (int | None): Best-effort minimum visible cell width for right text.
        left_pad (int | None): If not None and left text is present, render this many rule cells at far left,
            followed by one space, before the left text. `0` means just one separating space. `None` means no pad.
        right_pad (int | None): If not None and right text is present, render one space after the right text,
            followed by this many rule cells at far right. `0` means just one separating space. `None` means no pad.
    """

    def __init__(
            self,
            title: str | Text = '',
            *,
            left: str | Text | None = None,
            center: str | Text | None = None,
            right: str | Text | None = None,
            characters: str = '─',
            style: str | Style = 'rule.line',
            end: str = '\n',
            align: AlignMethod = 'center',
            min_left_length: int | None = None,
            min_right_length: int | None = None,
            left_pad: int | None = None,
            right_pad: int | None = None,
    ) -> None:
        if cell_len(characters) < 1:
            raise ValueError("'characters' argument must have a cell width of at least 1")
        if align not in ('left', 'center', 'right'):
            raise ValueError(f'invalid value for align, expected "left", "center", "right" (not {align!r})')
        if min_left_length is not None and min_left_length < 0:
            raise ValueError('min_left_length must be >= 0 or None')
        if min_right_length is not None and min_right_length < 0:
            raise ValueError('min_right_length must be >= 0 or None')
        if left_pad is not None and left_pad < 0:
            raise ValueError('left_pad must be >= 0 or None')
        if right_pad is not None and right_pad < 0:
            raise ValueError('right_pad must be >= 0 or None')

        super().__init__()

        self.title = title
        self.left = left
        self.center = center
        self.right = right
        self.characters = characters
        self.style = style
        self.end = end
        self.align = align
        self.min_left_length = min_left_length
        self.min_right_length = min_right_length
        self.left_pad = left_pad
        self.right_pad = right_pad

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.title!r}, {self.characters!r})'

    @staticmethod
    def _is_blank_title(title: str | Text | None) -> bool:
        if title is None:
            return True

        if isinstance(title, Text):
            return title.plain == ''

        return title == ''

    @staticmethod
    def _copy_clean_text(text: Text | None) -> Text | None:
        if text is None:
            return None

        text = text.copy()
        text.plain = text.plain.replace('\n', ' ')
        text.expand_tabs()

        if text.cell_len <= 0:
            return None

        return text

    @staticmethod
    def _truncate_text(text: Text | None, width: int) -> Text | None:
        if text is None or width <= 0:
            return None

        text = text.copy()
        text.truncate(width, overflow='ellipsis')

        if text.cell_len <= 0:
            return None

        return text

    @staticmethod
    def _allocate_evenly(budget: int, capacities: tuple[int, ...]) -> list[int]:
        """Allocate up to `budget` cells as evenly as possible across capped buckets."""

        budget = max(0, budget)
        allocations = [0 for _ in capacities]
        active = {index for index, capacity in enumerate(capacities) if capacity > 0}

        while budget > 0 and active:
            share = max(1, budget // len(active))

            for index in list(active):
                if budget <= 0:
                    break

                remaining_capacity = capacities[index] - allocations[index]
                take = min(remaining_capacity, share, budget)

                allocations[index] += take
                budget -= take

                if allocations[index] >= capacities[index]:
                    active.remove(index)

        return allocations

    @classmethod
    def _allocate_text_widths(
            cls,
            *,
            width: int,
            left_width: int,
            center_width: int,
            right_width: int,
            min_left_length: int | None,
            min_right_length: int | None,
    ) -> tuple[int, int, int]:
        """
        Return text-only widths for left, center, right.

        Policy:
        - Only legacy/single title: preserve Rich-ish spacing behavior.
        - Left + right, no center: distribute evenly.
        - Center + one side: center gets priority, except requested side minimum.
        - All three: reserve requested side minimums best-effort, fit center if possible, then distribute remaining room
          evenly between left and right.
        """

        width = max(0, width)

        has_left = left_width > 0
        has_center = center_width > 0
        has_right = right_width > 0

        present_count = int(has_left) + int(has_center) + int(has_right)
        if present_count == 0 or width <= 0:
            return 0, 0, 0

        min_left = min(left_width, min_left_length or 0)
        min_right = min(right_width, min_right_length or 0)

        # Preserve approximately the original Rule behavior for single-title cases: leave room for line + separator
        # space where possible.
        if present_count == 1:
            if has_center:
                return 0, min(center_width, max(0, width - 4)), 0
            if has_left:
                return min(left_width, max(0, width - 2)), 0, 0
            return 0, 0, min(right_width, max(0, width - 2))

        # Left + right, no center: distribute width evenly.
        if not has_center:
            left_alloc, right_alloc = cls._allocate_evenly(
                width,
                (min_left, min_right),
            )
            remaining = width - left_alloc - right_alloc

            left_extra, right_extra = cls._allocate_evenly(
                remaining,
                (left_width - left_alloc, right_width - right_alloc),
            )

            return left_alloc + left_extra, 0, right_alloc + right_extra

        # Center + left only: center hogs, except left minimum.
        if has_left and not has_right:
            left_alloc = min(min_left, max(0, width - 1))
            center_alloc = min(center_width, width - left_alloc)
            left_alloc = min(left_width, width - center_alloc)
            return left_alloc, center_alloc, 0

        # Center + right only: center hogs, except right minimum.
        if has_right and not has_left:
            right_alloc = min(min_right, max(0, width - 1))
            center_alloc = min(center_width, width - right_alloc)
            right_alloc = min(right_width, width - center_alloc)
            return 0, center_alloc, right_alloc

        # All three.
        # First: best-effort side minima while trying to leave at least 1 cell for center if possible.
        side_min_budget = max(0, width - 1)
        left_alloc, right_alloc = cls._allocate_evenly(
            side_min_budget,
            (min_left, min_right),
        )

        # Then center takes as much as it can.
        center_alloc = min(center_width, width - left_alloc - right_alloc)

        # Finally distribute any remaining width evenly between left and right.
        remaining = width - left_alloc - center_alloc - right_alloc
        left_extra, right_extra = cls._allocate_evenly(
            remaining,
            (left_width - left_alloc, right_width - right_alloc),
        )

        return left_alloc + left_extra, center_alloc, right_alloc + right_extra

    @classmethod
    def _rule_chars(cls, characters: str, width: int) -> str:
        if width <= 0:
            return ''

        chars_len = cell_len(characters)
        return set_cell_size(characters * ((width // chars_len) + 1), width)

    @classmethod
    def _rule_gap(
            cls,
            characters: str,
            width: int,
            *,
            style_left_is_text: bool = False,
            style_right_is_text: bool = False,
    ) -> str:
        """
        Return a rule gap.

        If the gap touches text, spend one cell as a visual separator space when
        possible. Examples with '-':

            gap(5, left_text=True, right_text=True)  -> " --- "
            gap(5, left_text=True, right_text=False) -> " ----"
            gap(5, left_text=False, right_text=True) -> "---- "
        """

        if width <= 0:
            return ''

        left_space = style_left_is_text
        right_space = style_right_is_text

        if left_space and right_space:
            if width == 1:
                return ' '
            return ' ' + cls._rule_chars(characters, width - 2) + ' '

        if left_space:
            return ' ' + cls._rule_chars(characters, width - 1)

        if right_space:
            return cls._rule_chars(characters, width - 1) + ' '

        return cls._rule_chars(characters, width)

    @classmethod
    def _left_pad_text(cls, characters: str, left_pad: int) -> str:
        return cls._rule_chars(characters, left_pad) + ' '

    @classmethod
    def _right_pad_text(cls, characters: str, right_pad: int) -> str:
        return ' ' + cls._rule_chars(characters, right_pad)

    @classmethod
    def render_rule_text(
            cls,
            *,
            width: int,
            characters: str,
            style: str | Style,
            end: str = '\n',
            left: Text | None = None,
            center: Text | None = None,
            right: Text | None = None,
            min_left_length: int | None = None,
            min_right_length: int | None = None,
            left_pad: int | None = None,
            right_pad: int | None = None,
    ) -> Text:
        """
        Render a rule from already-rendered Text slots.

        This is intentionally independent of Console so it can be unit tested.
        """

        width = max(0, width)

        if cell_len(characters) < 1:
            raise ValueError("'characters' argument must have a cell width of at least 1")
        if left_pad is not None and left_pad < 0:
            raise ValueError('left_pad must be >= 0 or None')
        if right_pad is not None and right_pad < 0:
            raise ValueError('right_pad must be >= 0 or None')

        left = cls._copy_clean_text(left)
        center = cls._copy_clean_text(center)
        right = cls._copy_clean_text(right)

        use_left_pad = left_pad is not None and left is not None
        use_right_pad = right_pad is not None and right is not None

        left_pad_width = (left_pad + 1) if use_left_pad else 0  # type: ignore[operator]
        right_pad_width = (right_pad + 1) if use_right_pad else 0  # type: ignore[operator]

        layout_width = max(0, width - left_pad_width - right_pad_width)

        def wrap_with_side_padding(inner_text: Text) -> Text:
            if not use_left_pad and not use_right_pad:
                inner_text.end = end
                inner_text.plain = set_cell_size(inner_text.plain, width)
                return inner_text

            outer_text = Text(end=end)

            if use_left_pad:
                outer_text.append(
                    cls._left_pad_text(characters, check.not_none(left_pad)),
                    style,
                )

            outer_text.append_text(inner_text)

            if use_right_pad:
                outer_text.append(
                    cls._right_pad_text(characters, check.not_none(right_pad)),
                    style,
                )

            outer_text.plain = set_cell_size(outer_text.plain, width)
            return outer_text

        if not left and not center and not right:
            rule_text = Text(cls._rule_chars(characters, layout_width), style, end='')
            rule_text.truncate(layout_width)
            rule_text.plain = set_cell_size(rule_text.plain, layout_width)
            return wrap_with_side_padding(rule_text)

        left_width, center_width, right_width = cls._allocate_text_widths(
            width=layout_width,
            left_width=left.cell_len if left else 0,
            center_width=center.cell_len if center else 0,
            right_width=right.cell_len if right else 0,
            min_left_length=min_left_length,
            min_right_length=min_right_length,
        )

        left = cls._truncate_text(left, left_width)
        center = cls._truncate_text(center, center_width)
        right = cls._truncate_text(right, right_width)

        left_width = left.cell_len if left else 0
        center_width = center.cell_len if center else 0
        right_width = right.cell_len if right else 0

        if not left and not center and not right:
            rule_text = Text(cls._rule_chars(characters, layout_width), style, end='')
            rule_text.truncate(layout_width)
            rule_text.plain = set_cell_size(rule_text.plain, layout_width)
            return wrap_with_side_padding(rule_text)

        rule_text = Text(end='')

        def append_gap(
            gap_width: int,
            *,
            left_text: bool = False,
            right_text: bool = False,
        ) -> None:
            if gap_width > 0:
                rule_text.append(
                    cls._rule_gap(
                        characters,
                        gap_width,
                        style_left_is_text=left_text,
                        style_right_is_text=right_text,
                    ),
                    style,
                )

        def append_text(text: Text | None) -> None:
            if text is not None:
                rule_text.append_text(text)

        # Single slot cases.

        if left and not center and not right:
            append_text(left)
            append_gap(layout_width - left_width, left_text=True)

        elif right and not left and not center:
            append_gap(layout_width - right_width, right_text=True)
            append_text(right)

        elif center and not left and not right:
            start = (layout_width - center_width) // 2
            append_gap(start, right_text=True)
            append_text(center)
            append_gap(layout_width - start - center_width, left_text=True)

        # Two slot cases.

        elif left and right and not center:
            append_text(left)
            append_gap(layout_width - left_width - right_width, left_text=True, right_text=True)
            append_text(right)

        elif left and center and not right:
            target_center_start = (layout_width - center_width) // 2
            center_start = max(left_width, target_center_start)
            center_start = min(center_start, layout_width - center_width)

            append_text(left)
            append_gap(center_start - left_width, left_text=True, right_text=True)
            append_text(center)
            append_gap(layout_width - center_start - center_width, left_text=True)

        elif center and right and not left:
            target_center_start = (layout_width - center_width) // 2
            center_start = min(target_center_start, layout_width - center_width - right_width)
            center_start = max(0, center_start)

            append_gap(center_start, right_text=True)
            append_text(center)
            append_gap(
                layout_width - center_start - center_width - right_width,
                left_text=True,
                right_text=True,
            )
            append_text(right)

        # Three slot case.

        else:
            left = check.not_none(left)
            center = check.not_none(center)
            right = check.not_none(right)

            target_center_start = (layout_width - center_width) // 2
            center_start = max(left_width, target_center_start)
            center_start = min(center_start, layout_width - center_width - right_width)

            append_text(left)
            append_gap(center_start - left_width, left_text=True, right_text=True)
            append_text(center)
            append_gap(
                layout_width - center_start - center_width - right_width,
                left_text=True,
                right_text=True,
            )
            append_text(right)

        rule_text.plain = set_cell_size(rule_text.plain, layout_width)
        return wrap_with_side_padding(rule_text)

    def _render_title(
        self,
        console: Console,
        title: str | Text | None,
    ) -> Text | None:
        if self._is_blank_title(title):
            return None

        if isinstance(title, Text):
            return title.copy()

        return console.render_str(check.not_none(title), style='rule.text')

    def __rich_console__(
            self,
            console: Console,
            options: ConsoleOptions,
    ) -> RenderResult:
        width = options.max_width

        characters = (
            '-'
            if (options.ascii_only and not self.characters.isascii())
            else self.characters
        )

        left = self.left
        center = self.center
        right = self.right

        # Backwards compatibility: legacy `title` maps into the `align` slot, unless that slot was explicitly supplied.
        if not self._is_blank_title(self.title):
            if self.align == 'left' and left is None:
                left = self.title
            elif self.align == 'center' and center is None:
                center = self.title
            elif self.align == 'right' and right is None:
                right = self.title

        yield self.render_rule_text(
            width=width,
            characters=characters,
            style=self.style,
            end=self.end,
            left=self._render_title(console, left),
            center=self._render_title(console, center),
            right=self._render_title(console, right),
            min_left_length=self.min_left_length,
            min_right_length=self.min_right_length,
            left_pad=self.left_pad,
            right_pad=self.right_pad,
        )

    def _rule_line(self, chars_len: int, width: int) -> Text:
        rule_text = Text(self.characters * ((width // chars_len) + 1), self.style)
        rule_text.truncate(width)
        rule_text.plain = set_cell_size(rule_text.plain, width)
        return rule_text

    def __rich_measure__(
            self,
            console: Console,
            options: ConsoleOptions,
    ) -> Measurement:
        return Measurement(1, 1)
