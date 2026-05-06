"""Comprehensive test suite for fixdocstrings tool."""
import textwrap

import pytest

from ..fixdocstrings import DocstringFixer


def normalize_indentation(s: str) -> str:
    """Remove common leading indentation from a string."""

    return textwrap.dedent(s)


class TestSingleLineDocstrings:
    """Test single-line docstring formatting."""

    def test_short_module_docstring_stays_single_line(self) -> None:
        """Short module docstrings should remain on a single line."""

        src = '"""Short module docstring"""\n'
        expected = '"""Short module docstring"""\n'
        fixer = DocstringFixer(src)
        result = fixer.fix()
        assert result == expected

    def test_short_class_docstring_stays_single_line(self) -> None:
        """Short class docstrings should remain on a single line."""

        src = normalize_indentation('''
            class Foo:
                """Short"""
                pass
        ''').lstrip()

        expected = normalize_indentation('''
            class Foo:
                """Short"""

                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()
        assert result == expected

    def test_short_function_docstring_stays_single_line(self) -> None:
        """Short function docstrings should remain on a single line."""

        src = normalize_indentation('''
            def foo():
                """Returns nothing"""
                pass
        ''').lstrip()

        expected = normalize_indentation('''
            def foo():
                """Returns nothing"""

                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()
        assert result == expected

    def test_short_method_docstring_stays_single_line(self) -> None:
        """Short method docstrings should remain on a single line."""

        src = normalize_indentation('''
            class Foo:
                """Class doc"""

                def method(self):
                    """Method doc"""
                    pass
        ''').lstrip()

        expected = normalize_indentation('''
            class Foo:
                """Class doc"""

                def method(self):
                    """Method doc"""

                    pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()
        assert result == expected

    def test_120_char_limit_single_line(self) -> None:
        """Docstrings that fit exactly on 120 chars should stay single-line."""

        # 120 chars total including indentation and triple-quotes
        # 4 spaces indent + 3 (""") + content + 3 (""") = 120
        # So content should be 120 - 4 - 6 = 110 chars
        content = 'x' * 110
        src = f'def foo():\n    """{content}"""\n    pass\n'
        fixer = DocstringFixer(src)
        result = fixer.fix()
        # Should stay single-line (exactly 120 chars)
        lines = result.split('\n')
        docstring_line = next(l for l in lines if content in l)
        # The line should be exactly 120 chars or less
        assert len(docstring_line) <= 120
        # And it should be single-line format
        assert f'"""{content}"""' in result


class TestMultiLineDocstrings:
    """Test multi-line docstring formatting."""

    def test_long_single_line_converts_to_multiline(self) -> None:
        """Long single-line docstrings should be converted to multi-line."""

        # Create a docstring that's definitely too long
        content = (
            'This is a very long docstring that definitely exceeds 120 characters '
            'when including indentation and triple-quotes.'
        )
        src = f'def foo():\n    """{content}"""\n    pass\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should be multi-line with triple-quotes on separate lines
        assert '"""\n' in result
        assert f'{content}\n    """' in result

    def test_multiline_docstring_preserved(self) -> None:
        """Multi-line docstrings should keep their structure."""

        src = normalize_indentation('''
            def foo():
                """
                This is a multi-line docstring.
                It has multiple lines.
                """
                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should still be multi-line
        assert '"""\n' in result
        assert 'This is a multi-line docstring.' in result
        assert 'It has multiple lines.' in result

    def test_multiline_with_internal_formatting(self) -> None:
        """Multi-line docstrings with internal formatting should preserve it."""

        src = normalize_indentation('''
            def foo():
                """
                Summary line.

                Detailed explanation with:
                    - Bullet points
                    - More bullets

                And a conclusion.
                """
                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Internal structure should be preserved
        assert 'Summary line.' in result
        assert '    - Bullet points' in result
        assert 'And a conclusion.' in result


class TestBlankLineAfterDocstring:
    """Test that blank lines are added after class/function docstrings (but not module docstrings)."""

    def test_blank_line_not_added_after_module_docstring(self) -> None:
        """Blank line should NOT be added after module docstring."""

        src = normalize_indentation('''
            """Module doc"""
            import os
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should NOT have blank line between docstring and import
        assert '"""Module doc"""\nimport os' in result

    def test_blank_line_added_after_class_docstring(self) -> None:
        """Blank line should be added after class docstring."""

        src = normalize_indentation('''
            class Foo:
                """Class doc"""
                def method(self):
                    pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        lines = result.split('\n')
        # Find the docstring line
        doc_idx = next(i for i, line in enumerate(lines) if 'Class doc' in line)
        # Next line should be empty (blank line)
        assert lines[doc_idx + 1].strip() == ''

    def test_blank_line_added_after_function_docstring(self) -> None:
        """Blank line should be added after function docstring."""

        src = normalize_indentation('''
            def foo():
                """Function doc"""
                return 42
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        lines = result.split('\n')
        doc_idx = next(i for i, line in enumerate(lines) if 'Function doc' in line)
        assert lines[doc_idx + 1].strip() == ''

    def test_existing_blank_line_preserved(self) -> None:
        """Existing blank lines after docstrings should be preserved."""

        src = normalize_indentation('''
            def foo():
                """Function doc"""

                return 42
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should still have the blank line
        assert '"""Function doc"""\n\n    return 42' in result


class TestNonDocstringStrings:
    """Test that regular strings are not modified."""

    def test_regular_string_untouched(self) -> None:
        """Regular triple-quoted strings should not be modified."""

        src = normalize_indentation('''
            def foo():
                """Real docstring"""

                x = """This is a regular string"""
                return x
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Regular string should be unchanged
        assert 'x = """This is a regular string"""' in result

    def test_long_regular_string_untouched(self) -> None:
        """Long regular strings should not be converted to multi-line."""

        long_str = 'x' * 150
        src = f'x = """{long_str}"""\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should be unchanged
        assert f'x = """{long_str}"""' in result

    def test_multiline_regular_string_untouched(self) -> None:
        """Multi-line regular strings should not be modified."""

        src = normalize_indentation('''
            x = """Line 1
            Line 2
            Line 3"""
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should be unchanged
        assert result == src


class TestIndentation:
    """Test correct handling of indentation."""

    def test_closing_triplequote_preserves_indentation(self) -> None:
        """Closing triple-quotes should be indented to match opening quotes."""

        src = normalize_indentation('''
            class Foo:
                """
                Multi-line docstring that is quite long and exceeds the character limit.
                It has multiple lines to ensure it stays multi-line.
                """
                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Closing triple-quotes should be at the same indentation as opening quotes
        assert '    """\n' in result
        assert '    """' in result
        # Verify the closing quotes are indented (not at column 0)
        lines = result.split('\n')
        closing_line = next(l for l in lines if l.strip() == '"""' and '"""' not in l.replace('"""', '', 1))
        assert closing_line.startswith('    ')  # Should have 4 spaces of indentation

    def test_nested_class_indentation(self) -> None:
        """Nested classes should handle indentation correctly."""

        src = normalize_indentation('''
            class Outer:
                """Outer class"""

                class Inner:
                    """Inner class"""

                    def method(self):
                        """Method doc"""
                        pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # All docstrings should be present with blank lines
        assert '"""Outer class"""\n\n' in result
        assert '"""Inner class"""\n\n' in result
        assert '"""Method doc"""\n\n' in result

    def test_deeply_indented_function(self) -> None:
        """Deeply indented functions should calculate width correctly."""

        # 8 spaces indent + long docstring should convert to multi-line
        content = 'x' * 100  # 100 + 6 (""") + 8 (indent) = 114, but create longer to be sure
        content = 'x' * 120
        src = f'        def foo():\n            """{content}"""\n            pass\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should be multi-line due to indent + content exceeding 120
        assert '"""\n' in result


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_async_function_docstring(self) -> None:
        """Async function docstrings should be handled."""

        src = normalize_indentation('''
            async def foo():
                """Async function"""
                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        assert '"""Async function"""\n\n' in result

    def test_single_quote_docstrings(self) -> None:
        """Triple single-quote docstrings should be handled."""

        src = "def foo():\n    '''Single quote docstring'''\n    pass\n"

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should add blank line
        assert "'''Single quote docstring'''\n\n" in result

    def test_raw_string_docstring(self) -> None:
        """Raw string docstrings should be handled."""

        src = 'def foo():\n    r"""Raw docstring with \\n escape"""\n    pass\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should preserve the r prefix
        assert 'r"""Raw docstring with \\n escape"""\n\n' in result

    def test_empty_module(self) -> None:
        """Empty modules should not crash."""

        src = ''

        fixer = DocstringFixer(src)
        result = fixer.fix()

        assert result == src

    def test_module_with_only_comments(self) -> None:
        """Modules with only comments should work."""

        src = '# Just a comment\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        assert result == src

    def test_syntax_error_returns_original(self) -> None:
        """Files with syntax errors should return original source."""

        src = 'def foo(\n'  # Incomplete function

        fixer = DocstringFixer(src)
        result = fixer.fix()

        assert result == src

    def test_single_line_docstring_without_newline(self) -> None:
        """Single-line docstrings at EOF without newline should work."""

        src = '"""Module docstring"""'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should add blank line even though there's no code after
        assert result.startswith('"""Module docstring"""')

    def test_multiple_classes_and_functions(self) -> None:
        """Complex modules with multiple elements should all be fixed."""

        src = normalize_indentation('''
            """Module docstring"""
            class A:
                """Class A"""
                def method_a(self):
                    """Method A"""
                    pass

            class B:
                """Class B"""
                def method_b(self):
                    """Method B"""
                    pass

            def standalone():
                """Standalone function"""
                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Module docstring should NOT have blank line after it
        assert '"""Module docstring"""\nclass A:' in result

        # All class/function docstrings should have blank lines after them
        class_function_docstrings = [
            '"""Class A"""',
            '"""Method A"""',
            '"""Class B"""',
            '"""Method B"""',
            '"""Standalone function"""',
        ]

        for docstring in class_function_docstrings:
            assert docstring in result
            # Check that there's a blank line after each
            assert f'{docstring}\n\n' in result


class TestWhitespacePreservation:
    """Test that non-docstring whitespace is preserved."""

    def test_comments_preserved(self) -> None:
        """Comments should be preserved exactly."""

        src = normalize_indentation('''
            # This is a comment
            def foo():
                """Docstring"""
                # Another comment
                pass  # Inline comment
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        assert '# This is a comment' in result
        assert '# Another comment' in result
        assert '# Inline comment' in result

    def test_blank_lines_between_functions_preserved(self) -> None:
        """Blank lines between functions should be preserved."""

        src = normalize_indentation('''
            def foo():
                """First"""
                pass


            def bar():
                """Second"""
                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # The double blank line between functions should still be there
        assert 'pass\n\n\ndef bar' in result

    def test_trailing_whitespace_on_other_lines_preserved(self) -> None:
        """Trailing whitespace on non-docstring lines should be preserved."""

        # Note: This is a bit tricky to test since we want to preserve source exactly
        src = 'def foo():\n    """Doc"""\n    x = 5  \n    return x\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # The trailing spaces after "x = 5" should be preserved
        assert 'x = 5  \n' in result


class TestDocstringContent:
    """Test various docstring content patterns."""

    def test_docstring_with_quotes_inside(self) -> None:
        """Docstrings containing quotes should be handled."""

        src = '''def foo():\n    """This has "quotes" inside"""\n    pass\n'''

        fixer = DocstringFixer(src)
        result = fixer.fix()

        assert '''"""This has "quotes" inside"""''' in result

    def test_docstring_with_newlines_in_content(self) -> None:
        """Docstrings with explicit newlines should be multi-line."""

        src = normalize_indentation('''
            def foo():
                """Line 1
                Line 2"""
                pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should be formatted as multi-line
        assert '"""\n' in result
        assert 'Line 1\n' in result
        assert 'Line 2\n    """' in result

    def test_empty_docstring(self) -> None:
        """Empty docstrings should be handled."""

        src = 'def foo():\n    """"""\n    pass\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Empty docstring should stay as-is (it's already minimal)
        assert '""""""' in result


class TestRealWorldExamples:
    """Test real-world docstring patterns."""

    def test_numpy_style_docstring(self) -> None:
        """Numpy-style docstrings should be formatted correctly."""

        src = normalize_indentation('''
            def function(arg1, arg2):
                """
                Summary line.

                Parameters
                ----------
                arg1 : int
                    Description of arg1
                arg2 : str
                    Description of arg2

                Returns
                -------
                bool
                    Description of return value
                """
                return True
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should preserve the numpy-style structure
        assert 'Parameters\n' in result
        assert 'Returns\n' in result
        assert '----------' in result
        # Should have blank line after
        assert '"""\n\n    return True' in result

    def test_google_style_docstring(self) -> None:
        """Google-style docstrings should be formatted correctly."""

        src = normalize_indentation('''
            def function(arg1, arg2):
                """
                Summary line.

                Args:
                    arg1: Description
                    arg2: Description

                Returns:
                    Description of return value
                """
                return True
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should preserve the google-style structure
        assert 'Args:' in result
        assert 'Returns:' in result
        assert '"""\n\n    return True' in result


@pytest.mark.parametrize('prefix', ['r', 'R', 'u', 'U', 'f', 'F', 'b', 'B', 'br', 'rb', 'fr', 'rf'])
def test_string_prefixes(prefix: str) -> None:
    """Test that various string prefixes are handled correctly."""

    # Skip f-strings as they can't be docstrings (they're evaluated)
    if 'f' in prefix.lower():
        pytest.skip('f-strings cannot be docstrings')

    src = f'def foo():\n    {prefix}"""Docstring"""\n    pass\n'

    fixer = DocstringFixer(src)
    result = fixer.fix()

    # Prefix should be preserved
    assert f'{prefix}"""Docstring"""' in result


class TestEndOfFile:
    """Test that docstrings at the end of file don't add extra newlines."""

    def test_function_docstring_at_eof(self) -> None:
        """Function docstring at EOF should only have one trailing newline."""

        src = 'def foo():\n    """Docstring"""\n    pass\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should have blank line after docstring, but only one newline at EOF
        assert result == 'def foo():\n    """Docstring"""\n\n    pass\n'
        # Should NOT end with double newline
        assert not result.endswith('\n\n')

    def test_class_docstring_at_eof(self) -> None:
        """Class docstring at EOF should only have one trailing newline."""

        src = 'class Foo:\n    """Class docstring"""\n    pass\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should have blank line after docstring, but only one newline at EOF
        assert result == 'class Foo:\n    """Class docstring"""\n\n    pass\n'
        assert not result.endswith('\n\n')

    def test_method_docstring_at_eof(self) -> None:
        """Method ending the file should only have one trailing newline."""

        src = normalize_indentation('''
            class Foo:
                """Class doc"""

                def method(self):
                    """Method doc"""
                    pass
        ''').lstrip()

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should NOT end with double newline
        assert not result.endswith('\n\n')
        # Should end with exactly one newline
        assert result.endswith('\n')
        assert result.endswith('pass\n')

    def test_empty_function_with_only_docstring_at_eof(self) -> None:
        """Function with only a docstring at EOF should only have one trailing newline."""

        src = 'def foo():\n    """Just a docstring"""\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Should NOT end with double newline
        assert not result.endswith('\n\n')
        # Should end with exactly one newline
        assert result.endswith('\n')

    def test_module_docstring_only_at_eof(self) -> None:
        """Module with only a docstring should keep one trailing newline."""

        src = '"""Module docstring"""\n'

        fixer = DocstringFixer(src)
        result = fixer.fix()

        # Module docstrings don't get blank lines, so should be unchanged
        assert result == src
        assert not result.endswith('\n\n')
