#!/usr/bin/env python3
"""
junit_gha_summary.py

Pure-stdlib JUnit XML -> GitHub Actions job summary + optional annotations.

Usage:
    python .github/scripts/junit_gha_summary.py test-results/*.xml \
        --annotations \
        --max-annotations 50 \
        --fail-on-failure

====

https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands

====

name: ci

on:
  pull_request:
  push:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          python -m pytest --junitxml=.reports/junit.xml

      - name: Publish test summary
        if: always()
        run: |
          python .github/scripts/junit_gha_summary.py '.reports/*.xml' \
            --annotations \
            --max-annotations 50
"""

from __future__ import annotations

import argparse
import dataclasses as dc
import glob
import os
import pathlib
import sys
import typing as ta
import xml.etree.ElementTree as ET
from collections import defaultdict


# ---------------------------------------------------------------------------
# GitHub Actions helpers


def _gha_escape_data(s: object) -> str:
    # Escaping convention used by the Actions command protocol.
    return (
        str(s)
        .replace('%', '%25')
        .replace('\r', '%0D')
        .replace('\n', '%0A')
    )


def _gha_escape_prop(s: object) -> str:
    return (
        _gha_escape_data(s)
        .replace(':', '%3A')
        .replace(',', '%2C')
    )


def gha_command(name: str, message: str = '', **props: object) -> None:
    """
    Emit a GitHub Actions workflow command to stdout.

    Example:
        gha_command("error", "boom", file="tests/test_foo.py", line=12)
    """
    prop_s = ''
    clean_props = {k: v for k, v in props.items() if v is not None and v != ''}
    if clean_props:
        prop_s = ' ' + ','.join(
            f'{k}={_gha_escape_prop(v)}'
            for k, v in clean_props.items()
        )

    print(f'::{name}{prop_s}::{_gha_escape_data(message)}', flush=True)


def append_step_summary(markdown: str) -> bool:
    """
    Append Markdown to GITHUB_STEP_SUMMARY when running in GitHub Actions.

    Returns True if written to the summary file, False if not in GHA.
    """
    path = os.environ.get('GITHUB_STEP_SUMMARY')
    if not path:
        return False

    with open(path, 'a', encoding='utf-8') as f:
        f.write(markdown)
        if not markdown.endswith('\n'):
            f.write('\n')
    return True


# ---------------------------------------------------------------------------
# JUnit parsing


@dc.dataclass(frozen=True)
class TestCase:
    source: pathlib.Path
    suite: str
    classname: str
    name: str
    time: float
    status: str  # passed | failure | error | skipped
    message: str = ''
    details: str = ''
    file: str = ''
    line: int | None = None

    @property
    def display_name(self) -> str:
        if self.classname:
            return f'{self.classname}.{self.name}'
        return self.name


def _local_name(tag: str) -> str:
    return tag.rsplit('}', 1)[-1]


def _float_attr(el: ET.Element, name: str, default: float = 0.0) -> float:
    try:
        return float(el.get(name, default))
    except (TypeError, ValueError):
        return default


def _int_attr_any(el: ET.Element, names: ta.Iterable[str]) -> int | None:
    for name in names:
        raw = el.get(name)
        if raw is None or raw == '':
            continue
        try:
            return int(raw)
        except ValueError:
            continue
    return None


def _first_direct_child(el: ET.Element, *names: str) -> ET.Element | None:
    wanted = set(names)
    for child in list(el):
        if _local_name(child.tag) in wanted:
            return child
    return None


def _all_text(el: ET.Element | None) -> str:
    if el is None:
        return ''
    return ''.join(el.itertext()).strip()


def _preview(s: str, n: int = 300) -> str:
    s = ' '.join(s.split())
    if len(s) <= n:
        return s
    return s[: n - 1] + '…'


def iter_testsuites(root: ET.Element) -> ta.Iterator[ET.Element]:
    if _local_name(root.tag) == 'testsuite':
        yield root

    for el in root.iter():
        if el is root:
            continue
        if _local_name(el.tag) == 'testsuite':
            yield el


def parse_junit_file(path: pathlib.Path) -> list[TestCase]:
    root = ET.parse(path).getroot()
    out: list[TestCase] = []

    for suite_el in iter_testsuites(root):
        suite_name = suite_el.get('name') or path.name

        # JUnit normally has testcases as direct children of testsuite.
        for tc_el in list(suite_el):
            if _local_name(tc_el.tag) != 'testcase':
                continue

            classname = tc_el.get('classname') or ''
            name = tc_el.get('name') or '<unnamed>'
            time = _float_attr(tc_el, 'time')

            status = 'passed'
            problem_el = _first_direct_child(tc_el, 'error')
            if problem_el is not None:
                status = 'error'
            else:
                problem_el = _first_direct_child(tc_el, 'failure')
                if problem_el is not None:
                    status = 'failure'
                else:
                    problem_el = _first_direct_child(tc_el, 'skipped')
                    if problem_el is not None:
                        status = 'skipped'

            details = _all_text(problem_el)
            message = ''
            if problem_el is not None:
                message = (
                    problem_el.get('message')
                    or problem_el.get('type')
                    or _preview(details)
                    or status
                )

            out.append(TestCase(
                source=path,
                suite=suite_name,
                classname=classname,
                name=name,
                time=time,
                status=status,
                message=message,
                details=details,
                file=tc_el.get('file') or '',
                line=_int_attr_any(tc_el, ('line', 'lineno')),
            ))

    return out


def expand_paths(patterns: list[str]) -> list[pathlib.Path]:
    paths: list[pathlib.Path] = []
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            paths.extend(pathlib.Path(m) for m in matches)
        else:
            paths.append(pathlib.Path(pattern))

    seen: set[pathlib.Path] = set()
    out: list[pathlib.Path] = []
    for p in paths:
        p = p.resolve()
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# ---------------------------------------------------------------------------
# Markdown rendering


def md_cell(s: object) -> str:
    """
    Escape enough for GitHub Markdown tables.
    """
    return (
        str(s)
        .replace('\\', '\\\\')
        .replace('|', '\\|')
        .replace('\r', '')
        .replace('\n', '<br>')
    )


def fmt_time(seconds: float) -> str:
    if seconds < 1:
        return f'{seconds * 1000:.0f} ms'
    if seconds < 60:
        return f'{seconds:.2f} s'
    m, s = divmod(seconds, 60)
    return f'{int(m)}m {s:.1f}s'


def fenced(text: str, lang: str = 'text') -> str:
    fence = '```'
    while fence in text:
        fence += '`'
    return f'{fence}{lang}\n{text.rstrip()}\n{fence}'


def count_status(cases: list[TestCase]) -> dict[str, int]:
    d = {
        'passed': 0,
        'failure': 0,
        'error': 0,
        'skipped': 0,
    }
    for c in cases:
        d[c.status] = d.get(c.status, 0) + 1
    return d


def render_summary(
    cases: list[TestCase],
    sources: list[pathlib.Path],
    *,
    max_failures: int = 25,
    max_detail_chars: int = 4000,
) -> str:
    counts = count_status(cases)
    total = len(cases)
    bad = counts['failure'] + counts['error']
    passed = counts['passed']
    skipped = counts['skipped']
    total_time = sum(c.time for c in cases)

    icon = '✅' if bad == 0 else '❌'
    pass_rate = 100.0 * passed / total if total else 0.0

    lines: list[str] = []
    lines.append(f'## {icon} Test results')
    lines.append('')
    lines.append('| Total | Passed | Failed | Errors | Skipped | Pass rate | Time |')
    lines.append('|---:|---:|---:|---:|---:|---:|---:|')
    lines.append(
        f"| {total} | {passed} | {counts['failure']} | {counts['error']} | "
        f"{skipped} | {pass_rate:.1f}% | {fmt_time(total_time)} |",
    )
    lines.append('')

    if sources:
        lines.append('<details>')
        lines.append('<summary>JUnit XML files</summary>')
        lines.append('')
        for p in sources:
            lines.append(f'- `{p}`')
        lines.append('')
        lines.append('</details>')
        lines.append('')

    by_suite: dict[str, list[TestCase]] = defaultdict(list)
    for c in cases:
        by_suite[c.suite].append(c)

    if by_suite:
        lines.append('### Suites')
        lines.append('')
        lines.append('| Suite | Total | Passed | Failed | Errors | Skipped | Time |')
        lines.append('|---|---:|---:|---:|---:|---:|---:|')

        def suite_sort_key(item: tuple[str, list[TestCase]]) -> tuple[int, int, str]:
            name, suite_cases = item
            sc = count_status(suite_cases)
            return (-(sc['failure'] + sc['error']), -len(suite_cases), name)

        for suite, suite_cases in sorted(by_suite.items(), key=suite_sort_key):
            sc = count_status(suite_cases)
            lines.append(
                f"| {md_cell(suite)} | {len(suite_cases)} | {sc['passed']} | "
                f"{sc['failure']} | {sc['error']} | {sc['skipped']} | "
                f"{fmt_time(sum(c.time for c in suite_cases))} |",
            )
        lines.append('')

    failed_cases = [c for c in cases if c.status in {'failure', 'error'}]
    if failed_cases:
        shown = failed_cases[:max_failures]

        lines.append('### Failed tests')
        lines.append('')
        lines.append('| Status | Test | Message | Location |')
        lines.append('|---|---|---|---|')

        for c in shown:
            location = ''
            if c.file:
                location = c.file
                if c.line:
                    location += f':{c.line}'

            lines.append(
                f'| {md_cell(c.status)} | `{md_cell(c.display_name)}` | '
                f'{md_cell(_preview(c.message, 500))} | {md_cell(location)} |',
            )

        if len(failed_cases) > len(shown):
            lines.append('')
            lines.append(f'_Showing {len(shown)} of {len(failed_cases)} failing tests._')

        lines.append('')
        lines.append('<details>')
        lines.append('<summary>Failure details</summary>')
        lines.append('')

        for c in shown:
            lines.append(f'#### `{c.display_name}`')
            lines.append('')
            if c.file:
                loc = c.file + (f':{c.line}' if c.line else '')
                lines.append(f'`{loc}`')
                lines.append('')

            detail = c.details or c.message
            if len(detail) > max_detail_chars:
                detail = detail[:max_detail_chars] + '\n… truncated …'

            lines.append(fenced(detail))
            lines.append('')

        lines.append('</details>')
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


# ---------------------------------------------------------------------------
# Annotations


def emit_failure_annotations(cases: list[TestCase], *, max_annotations: int) -> None:
    n = 0
    for c in cases:
        if c.status not in {'failure', 'error'}:
            continue
        if n >= max_annotations:
            gha_command(
                'warning',
                f'Not emitting further test annotations; hit max_annotations={max_annotations}',
                title='JUnit summary',
            )
            return

        gha_command(
            'error',
            c.message or c.status,
            title=f'{c.status}: {c.display_name}',
            file=c.file or None,
            line=c.line,
        )
        n += 1


# ---------------------------------------------------------------------------
# Main


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('xml', nargs='+', help='JUnit XML path(s) or glob(s)')
    ap.add_argument('--annotations', action='store_true')
    ap.add_argument('--max-annotations', type=int, default=50)
    ap.add_argument('--max-failures', type=int, default=25)
    ap.add_argument('--fail-on-failure', action='store_true')
    ap.add_argument('--allow-missing', action='store_true')
    ns = ap.parse_args(argv)

    paths = expand_paths(ns.xml)
    existing = [p for p in paths if p.exists()]

    if not existing:
        msg = 'No JUnit XML files found: ' + ', '.join(ns.xml)
        if ns.allow_missing:
            gha_command('warning', msg, title='JUnit summary')
            append_step_summary(f'## ⚠️ Test results\n\n{msg}\n')
            return 0
        gha_command('error', msg, title='JUnit summary')
        return 2

    cases: list[TestCase] = []
    parse_errors: list[tuple[pathlib.Path, Exception]] = []

    for p in existing:
        try:
            cases.extend(parse_junit_file(p))
        except Exception as e:
            parse_errors.append((p, e))

    if parse_errors:
        for p, e in parse_errors:
            gha_command('error', f'{type(e).__name__}: {e}', title='Failed to parse JUnit XML', file=str(p))
        return 2

    if ns.annotations:
        emit_failure_annotations(cases, max_annotations=ns.max_annotations)

    markdown = render_summary(cases, existing, max_failures=ns.max_failures)
    wrote_summary = append_step_summary(markdown)

    # Useful when running locally.
    if not wrote_summary:
        print(markdown)

    counts = count_status(cases)
    bad = counts['failure'] + counts['error']
    if ns.fail_on_failure and bad:
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
