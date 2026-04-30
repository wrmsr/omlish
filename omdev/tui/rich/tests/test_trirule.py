# @omlish-precheck-allow-any-unicode
import unittest

from rich.cells import cell_len
from rich.text import Text

from ..trirule import TriRule


class TriRuleRenderingTests(unittest.TestCase):
    def render(
        self,
        *,
        width: int,
        left: str | None = None,
        center: str | None = None,
        right: str | None = None,
        min_left_length: int | None = None,
        min_right_length: int | None = None,
    ) -> str:
        return TriRule.render_rule_text(
            width=width,
            characters='-',
            style='rule.line',
            end='',
            left=Text(left) if left is not None else None,
            center=Text(center) if center is not None else None,
            right=Text(right) if right is not None else None,
            min_left_length=min_left_length,
            min_right_length=min_right_length,
        ).plain

    def test_no_titles_renders_plain_rule(self) -> None:
        self.assertEqual(
            self.render(width=10),
            '----------',
        )

    def test_single_center_matches_expected_shape(self) -> None:
        self.assertEqual(
            self.render(width=20, center='TS'),
            '-------- TS --------',
        )

    def test_single_left_matches_expected_shape(self) -> None:
        self.assertEqual(
            self.render(width=10, left='abc'),
            'abc ------',
        )

    def test_single_right_matches_expected_shape(self) -> None:
        self.assertEqual(
            self.render(width=10, right='abc'),
            '------ abc',
        )

    def test_left_and_right_evenly_separated_when_both_fit(self) -> None:
        self.assertEqual(
            self.render(width=20, left='abc', right='xyz'),
            'abc ------------ xyz',
        )

    def test_left_center_right_keep_center_centered_when_all_fit(self) -> None:
        rendered = self.render(
            width=30,
            left='left',
            center='mid',
            right='right',
        )

        self.assertEqual(cell_len(rendered), 30)
        self.assertTrue(rendered.startswith('left'))
        self.assertTrue(rendered.endswith('right'))

        center_start = rendered.index('mid')
        self.assertEqual(center_start, (30 - len('mid')) // 2)

    def test_center_hogs_when_center_and_left_are_present(self) -> None:
        rendered = self.render(
            width=10,
            left='abcdef',
            center='CENTER-LONG',
        )

        self.assertEqual(cell_len(rendered), 10)
        self.assertNotIn('abcdef', rendered)
        self.assertIn('CENTER', rendered)
        self.assertTrue(rendered.endswith('…'))

    def test_center_hogs_when_center_and_right_are_present(self) -> None:
        rendered = self.render(
            width=10,
            center='CENTER-LONG',
            right='abcdef',
        )

        self.assertEqual(cell_len(rendered), 10)
        self.assertNotIn('abcdef', rendered)
        self.assertIn('CENTER', rendered)
        self.assertTrue(rendered.endswith('…'))

    def test_left_and_right_split_width_evenly_without_center(self) -> None:
        rendered = self.render(
            width=10,
            left='abcdefgh',
            right='ABCDEFGH',
        )

        self.assertEqual(cell_len(rendered), 10)
        self.assertEqual(rendered, 'abcd…ABCD…')

    def test_all_three_prioritizes_center_then_splits_sides(self) -> None:
        rendered = self.render(
            width=12,
            left='LLLL',
            center='CENTER',
            right='RRRR',
        )

        self.assertEqual(cell_len(rendered), 12)
        self.assertIn('CENTER', rendered)

        # No spare room for separator gaps here; sides split the remainder.
        self.assertTrue(rendered.startswith('LL'))
        self.assertTrue(rendered.endswith('RR…'))

    def test_min_left_and_right_are_best_effort(self) -> None:
        rendered = self.render(
            width=12,
            left='LLLLLL',
            center='CENTERLONG',
            right='RRRRRR',
            min_left_length=3,
            min_right_length=4,
        )

        self.assertEqual(cell_len(rendered), 12)

        # Best effort: left gets 3 cells, right gets 4 cells, center gets rest.
        self.assertTrue(rendered.startswith('LL…'))
        self.assertIn('CENT', rendered)
        self.assertTrue(rendered.endswith('RRR…'))

    def test_minimums_do_not_exceed_box(self) -> None:
        rendered = self.render(
            width=5,
            left='LLLLLL',
            center='CENTERLONG',
            right='RRRRRR',
            min_left_length=10,
            min_right_length=10,
        )

        self.assertEqual(cell_len(rendered), 5)

    def test_newlines_are_replaced(self) -> None:
        rendered = self.render(
            width=20,
            center='hello\nworld',
        )

        self.assertEqual(cell_len(rendered), 20)
        self.assertIn('hello world', rendered)
