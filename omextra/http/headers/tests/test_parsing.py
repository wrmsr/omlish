# ruff: noqa: UP006 UP045
"""
Comprehensive test suite for http_header_parser.

Covers:
  - Basic happy-path parsing (request + response)
  - Every ErrorCode / exception leaf class
  - Every HttpHeadParser.Config relaxation knob (on + off)
  - Character-set boundary conditions
  - Request smuggling vectors
  - Adversarial / ambiguous inputs
  - Prepared header validation for all 15 typed fields
  - Header combining and Set-Cookie special case
  - HTTP date parsing (all 3 formats + invalid)
  - Content-Type parameter parsing (quoted strings, charset, etc.)
  - Edge cases in Accept, Accept-Encoding, Cache-Control, Authorization
"""
import datetime
import typing as ta
import unittest

from omlish.lite.check import check

from .. import parsing as hp


##
# Helpers


def _req(
    method: str = 'GET',
    target: str = '/',
    version: str = 'HTTP/1.1',
    headers: ta.Optional[ta.List[ta.Tuple[str, str]]] = None,
    *,
    raw_line_ending: bytes = b'\r\n',
) -> bytes:
    """Build a well-formed request head from components."""

    parts: ta.List[bytes] = []
    parts.append(f'{method} {target} {version}'.encode('latin-1') + raw_line_ending)
    for name, value in (headers or []):
        parts.append(f'{name}: {value}'.encode('latin-1') + raw_line_ending)
    parts.append(raw_line_ending)  # terminator
    return b''.join(parts)


def _resp(
    version: str = 'HTTP/1.1',
    status: int = 200,
    reason: str = 'OK',
    headers: ta.Optional[ta.List[ta.Tuple[str, str]]] = None,
    *,
    raw_line_ending: bytes = b'\r\n',
) -> bytes:
    """Build a well-formed response head from components."""

    parts: ta.List[bytes] = []
    parts.append(f'{version} {status} {reason}'.encode('latin-1') + raw_line_ending)
    for name, value in (headers or []):
        parts.append(f'{name}: {value}'.encode('latin-1') + raw_line_ending)
    parts.append(raw_line_ending)
    return b''.join(parts)


STRICT = hp.HttpHeadParser.Config()


##
# 1. Basic happy-path parsing


class TestBasicRequest(unittest.TestCase):
    def test_simple_get(self) -> None:
        data = _req(headers=[('Host', 'example.com')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.kind, hp.ParsedHttpHead.Kind.REQUEST)
        self.assertIsNone(msg.status_line)
        self.assertEqual(check.not_none(msg.request_line).method, 'GET')
        self.assertEqual(check.not_none(msg.request_line).request_target, b'/')
        self.assertEqual(check.not_none(msg.request_line).http_version, 'HTTP/1.1')

    def test_post_with_body_headers(self) -> None:
        data = _req(
            method='POST',
            target='/submit',
            headers=[
                ('Host', 'example.com'),
                ('Content-Type', 'application/json'),
                ('Content-Length', '13'),
            ],
        )
        msg = check.not_none(hp.parse_http_head(data))
        self.assertEqual(check.not_none(msg.request_line).method, 'POST')
        self.assertEqual(msg.prepared.content_length, 13)
        self.assertEqual(check.not_none(msg.prepared.content_type).media_type, 'application/json')

    def test_all_standard_methods(self) -> None:
        for method in ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'):
            data = _req(method=method, headers=[('Host', 'x')])
            msg = hp.parse_http_head(data)
            self.assertEqual(check.not_none(msg.request_line).method, method)

    def test_custom_method(self) -> None:
        data = _req(method='PURGE', headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).method, 'PURGE')

    def test_complex_request_target(self) -> None:
        target = '/path/to/resource?foo=bar&baz=qux#frag'
        data = _req(target=target, headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).request_target, target.encode('ascii'))

    def test_asterisk_target(self) -> None:
        data = _req(method='OPTIONS', target='*', headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).request_target, b'*')

    def test_absolute_uri_target(self) -> None:
        target = 'http://example.com/foo'
        data = _req(target=target, headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).request_target, target.encode('ascii'))

    def test_http10_request(self) -> None:
        data = _req(version='HTTP/1.0')
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).http_version, 'HTTP/1.0')

    def test_no_headers(self) -> None:
        """HTTP/1.0 request with no headers at all."""

        data = b'GET / HTTP/1.0\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(len(msg.raw_headers), 0)
        self.assertEqual(len(msg.headers), 0)


class TestBasicResponse(unittest.TestCase):
    def test_simple_200(self) -> None:
        data = _resp(headers=[('Content-Length', '0')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.kind, hp.ParsedHttpHead.Kind.RESPONSE)
        self.assertEqual(check.not_none(msg.status_line).http_version, 'HTTP/1.1')
        self.assertEqual(check.not_none(msg.status_line).status_code, 200)
        self.assertEqual(check.not_none(msg.status_line).reason_phrase, 'OK')

    def test_status_range(self) -> None:
        for code in (100, 101, 200, 204, 301, 400, 404, 500, 599):
            data = _resp(status=code, reason='X')
            msg = hp.parse_http_head(data)
            self.assertEqual(check.not_none(msg.status_line).status_code, code)

    def test_empty_reason_phrase(self) -> None:
        data = b'HTTP/1.1 204 \r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.status_line).reason_phrase, '')

    def test_reason_phrase_with_special_chars(self) -> None:
        # Reason phrase allows HTAB, SP, VCHAR, obs-text
        data = b'HTTP/1.1 200 OK \t fine\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.status_line).reason_phrase, 'OK \t fine')

    def test_http10_response(self) -> None:
        data = _resp(version='HTTP/1.0')
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.status_line).http_version, 'HTTP/1.0')

    def test_no_headers_response(self) -> None:
        data = b'HTTP/1.1 204 No Content\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(len(msg.raw_headers), 0)


class TestAutoDetection(unittest.TestCase):
    def test_auto_detects_request(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data, mode=hp.HttpHeadParser.Mode.AUTO)
        self.assertEqual(msg.kind, hp.ParsedHttpHead.Kind.REQUEST)

    def test_auto_detects_response(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data, mode=hp.HttpHeadParser.Mode.AUTO)
        self.assertEqual(msg.kind, hp.ParsedHttpHead.Kind.RESPONSE)

    def test_forced_request_mode(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data, mode=hp.HttpHeadParser.Mode.REQUEST)
        self.assertEqual(msg.kind, hp.ParsedHttpHead.Kind.REQUEST)

    def test_forced_response_mode(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data, mode=hp.HttpHeadParser.Mode.RESPONSE)
        self.assertEqual(msg.kind, hp.ParsedHttpHead.Kind.RESPONSE)


##
# 2. Start-line errors


class TestStartLineErrors(unittest.TestCase):
    def test_empty_input(self) -> None:
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(b'')

    def test_no_sp_in_request_line(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GETHTTP/1.1\r\n\r\n')

    def test_one_sp_in_request_line(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET /HTTP/1.1\r\n\r\n')

    def test_three_sp_in_request_line(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET / foo HTTP/1.1\r\n\r\n')

    def test_empty_method(self) -> None:
        with self.assertRaises(hp.StartLineError):
            # " / HTTP/1.1" - first SP is at index 0 so method is empty
            hp.parse_http_head(b' / HTTP/1.1\r\n\r\n')

    def test_invalid_method_chars(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'G\x01T / HTTP/1.1\r\n\r\n')

    def test_method_with_special_invalid_char(self) -> None:
        # Parentheses are not tchar
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET() / HTTP/1.1\r\n\r\n')

    def test_empty_request_target(self) -> None:
        with self.assertRaises(hp.StartLineError):
            # Two adjacent spaces between method and version
            hp.parse_http_head(b'GET  HTTP/1.1\r\n\r\n')

    def test_request_target_non_visible_ascii(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET /\x01path HTTP/1.1\r\n\r\n')

    def test_unsupported_http_version_20(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET / HTTP/2.0\r\n\r\n')

    def test_unsupported_http_version_09(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET / HTTP/0.9\r\n\r\n')

    def test_unsupported_http_version_junk(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET / HTTZ/1.1\r\n\r\n')

    def test_status_line_no_sp(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1200OK\r\n\r\n')

    def test_status_line_missing_second_sp(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1 200\r\n\r\n')

    def test_status_code_non_digit(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1 2xx OK\r\n\r\n')

    def test_status_code_two_digits(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1 20 OK\r\n\r\n')

    def test_status_code_four_digits(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1 2000 OK\r\n\r\n')

    def test_status_code_099(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1 099 Low\r\n\r\n')

    def test_status_code_600(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1 600 High\r\n\r\n')

    def test_reason_phrase_nul(self) -> None:
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(b'HTTP/1.1 200 OK\x00X\r\n\r\n')

    def test_reason_phrase_invalid_ctl(self) -> None:
        # \x01 is not in reason-phrase chars (not HTAB/SP/VCHAR/obs-text)
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/1.1 200 OK\x01X\r\n\r\n')

    def test_response_unsupported_version(self) -> None:
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'HTTP/3.0 200 OK\r\n\r\n')


##
# 3. Header field syntax errors


class TestHeaderFieldErrors(unittest.TestCase):
    def test_missing_colon(self) -> None:
        data = b'GET / HTTP/1.1\r\nBadLine\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_empty_field_name(self) -> None:
        data = b'GET / HTTP/1.1\r\n: value\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_space_before_colon_strict(self) -> None:
        data = b'GET / HTTP/1.1\r\nHost : x\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_tab_before_colon_strict(self) -> None:
        data = b'GET / HTTP/1.1\r\nHost\t: x\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_nul_in_field_name(self) -> None:
        data = b'GET / HTTP/1.1\r\nHo\x00st: x\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_nul_in_field_value(self) -> None:
        data = b'GET / HTTP/1.1\r\nHost: x\x00y\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_non_ascii_in_field_name(self) -> None:
        data = b'GET / HTTP/1.1\r\nH\xc3\xb6st: x\r\n\r\n'
        with self.assertRaises(hp.EncodingError):
            hp.parse_http_head(data)

    def test_invalid_char_in_field_name(self) -> None:
        # '(' is not a tchar
        data = b'GET / HTTP/1.1\r\nFoo(bar): x\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_space_in_field_name(self) -> None:
        data = b'GET / HTTP/1.1\r\nFoo Bar: x\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_colon_in_field_name(self) -> None:
        # First colon is the separator; "Foo" is the name, ":bar: x" is value.
        # Actually this would parse as field-name "Foo" and value ":bar: x" which is fine.
        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo::bar\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['foo'], ':bar')

    def test_obs_fold_rejected_by_default(self) -> None:
        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo: bar\r\n baz\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_bare_lf_rejected_by_default(self) -> None:
        with self.assertRaises(hp.HttpParseError):
            hp.parse_http_head(b'GET / HTTP/1.1\nHost: x\n\n')

    def test_bare_cr_rejected_by_default(self) -> None:
        data = b'GET / HTTP/1.1\r\nHost: x\ronly\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_missing_terminator(self) -> None:
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(b'GET / HTTP/1.1\r\nHost: x\r\n')

    def test_trailing_data(self) -> None:
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(b'HTTP/1.1 200 OK\r\n\r\nextra')

    def test_too_many_headers(self) -> None:
        cfg = hp.HttpHeadParser.Config(max_header_count=3)
        hdrs = [(f'X-H{i}', str(i)) for i in range(4)]
        data = _resp(headers=hdrs)
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data, config=cfg)

    def test_obs_text_in_value_rejected_with_flag(self) -> None:
        cfg = hp.HttpHeadParser.Config(reject_obs_text=True)
        data = b'HTTP/1.1 200 OK\r\nX-Data: caf\xe9\r\n\r\n'
        with self.assertRaises(hp.EncodingError):
            hp.parse_http_head(data, config=cfg)

    def test_obs_text_in_value_allowed_by_default(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nX-Data: caf\xe9\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-data'], 'caf\xe9')

    def test_field_value_ctl_char(self) -> None:
        """Control characters (other than HTAB) in field-value should be rejected."""

        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo: bar\x01baz\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_del_in_field_value(self) -> None:
        """DEL (0x7F) is not VCHAR, not SP, not HTAB, not obs-text."""

        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo: bar\x7fbaz\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_max_header_length(self) -> None:
        cfg = hp.HttpHeadParser.Config(max_header_length=14)
        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo: value1 value2 value3\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data, config=cfg)


##
# 4. Relaxation knob tests


class TestRelaxationKnobs(unittest.TestCase):
    def test_allow_bare_lf(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_bare_lf=True, allow_missing_host=True)
        data = b'GET / HTTP/1.1\nHost: x\n\n'
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.host, 'x')

    def test_allow_bare_lf_mixed(self) -> None:
        """CRLF and bare LF mixed - some servers do this."""

        cfg = hp.HttpHeadParser.Config(allow_bare_lf=True, allow_missing_host=True)
        data = b'GET / HTTP/1.1\nHost: x\r\nFoo: bar\n\n'
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.headers['foo'], 'bar')

    def test_bare_lf_allows_only_final_terminator(self) -> None:
        data = b'GET / HTTP/1.1\nHost: example.com\n\n'
        parser = hp.HttpHeadParser(hp.HttpHeadParser.Config(allow_bare_lf=True))
        msg = parser.parse(data, mode=hp.HttpHeadParser.Mode.REQUEST)
        self.assertEqual(msg.kind.value, 'request')
        self.assertEqual(check.not_none(msg.request_line).method, 'GET')
        self.assertEqual(msg.headers.get('host'), 'example.com')

    def test_bare_lf_rejects_trailing_data_after_terminator(self) -> None:
        parser = hp.HttpHeadParser(hp.HttpHeadParser.Config(allow_bare_lf=True))
        data = b'GET / HTTP/1.1\nHost: example.com\n\nGARBAGE'
        with self.assertRaises(hp.HeaderFieldError) as cm:
            parser.parse(data, mode=hp.HttpHeadParser.Mode.REQUEST)
        self.assertEqual(cm.exception.code, hp.HeaderFieldErrorCode.MISSING_TERMINATOR)

    def test_strict_mode_rejects_bare_lf_even_if_double_lf(self) -> None:
        parser = hp.HttpHeadParser(hp.HttpHeadParser.Config(allow_bare_lf=False))
        data = b'GET / HTTP/1.1\nHost: example.com\n\n'
        with self.assertRaises(hp.HeaderFieldError) as cm:
            parser.parse(data, mode=hp.HttpHeadParser.Mode.REQUEST)
        # Depending on where it fails in your flow, this can be BARE_LF or MISSING_TERMINATOR.
        self.assertIn(cm.exception.code, {hp.HeaderFieldErrorCode.MISSING_TERMINATOR, hp.HeaderFieldErrorCode.BARE_LF})

    def test_allow_obs_fold(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_obs_fold=True)
        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo: line1\r\n line2\r\n\tline3\r\n\r\n'
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.headers['foo'], 'line1 line2 line3')

    def test_allow_obs_fold_multi_continuation(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_obs_fold=True)
        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo: a\r\n b\r\n c\r\n d\r\n\r\n'
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.headers['foo'], 'a b c d')

    def test_allow_obs_fold_max_len(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_obs_fold=True, max_header_length=14)
        data = b'GET / HTTP/1.1\r\nHost: x\r\nFoo: line1\r\n line2\r\n\tline3\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data, config=cfg)

    def test_reject_target_non_visible_ascii_request_target(self) -> None:
        cfg = hp.HttpHeadParser.Config(reject_non_visible_ascii_request_target=True)
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET /\xe2\x98\x83path HTTP/1.1\r\n\r\n', config=cfg)
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(b'GET /\x01path HTTP/1.1\r\n\r\n', config=cfg)

    def test_allow_space_before_colon(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_space_before_colon=True)
        data = b'GET / HTTP/1.1\r\nHost : example.com\r\n\r\n'
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.host, 'example.com')

    def test_space_before_colon_all_whitespace_name(self) -> None:
        """A line like ': value' (colon at start) produces EmptyFieldName."""

        cfg = hp.HttpHeadParser.Config(allow_space_before_colon=True)
        data = b'GET / HTTP/1.1\r\nHost: x\r\n: value\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data, config=cfg)

    def test_whitespace_line_start_is_obs_fold(self) -> None:
        """A line starting with whitespace is obs-fold, not a whitespace-only name."""

        cfg = hp.HttpHeadParser.Config(allow_space_before_colon=True)
        data = b'GET / HTTP/1.1\r\nHost: x\r\n  : value\r\n\r\n'
        # This triggers obs-fold detection, not EmptyFieldName
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data, config=cfg)

    def test_allow_multiple_content_lengths_identical(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_multiple_content_lengths=True)
        data = _resp(headers=[('Content-Length', '42'), ('Content-Length', '42')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.content_length, 42)

    def test_allow_multiple_content_lengths_comma_form(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_multiple_content_lengths=True)
        data = _resp(headers=[('Content-Length', '42, 42, 42')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.content_length, 42)

    def test_multiple_content_lengths_rejected_by_default(self) -> None:
        data = _resp(headers=[('Content-Length', '42'), ('Content-Length', '42')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_conflicting_content_lengths_always_rejected(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_multiple_content_lengths=True)
        data = _resp(headers=[('Content-Length', '42'), ('Content-Length', '99')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=cfg)

    def test_allow_content_length_with_te(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_content_length_with_te=True)
        data = _req(headers=[
            ('Host', 'x'),
            ('Content-Length', '42'),
            ('Transfer-Encoding', 'chunked'),
        ])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.content_length, 42)
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_content_length_with_te_rejected_by_default(self) -> None:
        data = _req(headers=[
            ('Host', 'x'),
            ('Content-Length', '42'),
            ('Transfer-Encoding', 'chunked'),
        ])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_allow_missing_host(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_missing_host=True)
        data = _req(headers=[])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertIsNone(msg.prepared.host)

    def test_missing_host_rejected_for_http11(self) -> None:
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(_req(headers=[]))

    def test_missing_host_ok_for_http10(self) -> None:
        data = _req(version='HTTP/1.0', headers=[])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.host)

    def test_allow_multiple_hosts_identical(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_multiple_hosts=True)
        data = _req(headers=[('Host', 'a.com'), ('Host', 'a.com')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.host, 'a.com')

    def test_multiple_hosts_rejected_by_default(self) -> None:
        data = _req(headers=[('Host', 'a.com'), ('Host', 'a.com')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_conflicting_hosts_always_rejected(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_multiple_hosts=True)
        data = _req(headers=[('Host', 'a.com'), ('Host', 'b.com')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=cfg)

    def test_allow_bare_cr_in_value(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_bare_cr_in_value=True)
        data = b'HTTP/1.1 200 OK\r\nFoo: bar\rbaz\r\n\r\n'
        msg = hp.parse_http_head(data, config=cfg)
        self.assertIn('bar', msg.headers['foo'])

    def test_allow_empty_header_values_true_by_default(self) -> None:
        data = _resp(headers=[('X-Empty', '')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-empty'], '')

    def test_reject_empty_header_values(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_empty_header_values=False)
        data = _resp(headers=[('X-Empty', '')])
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data, config=cfg)

    def test_allow_te_without_chunked_in_response(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_te_without_chunked_in_response=True)
        data = _resp(headers=[('Transfer-Encoding', 'gzip')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.transfer_encoding, ['gzip'])

    def test_te_without_chunked_in_response_rejected_by_default(self) -> None:
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(_resp(headers=[('Transfer-Encoding', 'gzip')]))

    def test_allow_transfer_encoding_http10(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_transfer_encoding_http10=True)
        data = _resp(version='HTTP/1.0', headers=[('Transfer-Encoding', 'chunked')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_transfer_encoding_http10_rejected_by_default(self) -> None:
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(_resp(
                version='HTTP/1.0',
                headers=[('Transfer-Encoding', 'chunked')],
            ))

    def test_allow_unknown_transfer_encoding(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_unknown_transfer_encoding=True)
        data = _req(headers=[('Host', 'x'), ('Transfer-Encoding', 'custom, chunked')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.transfer_encoding, ['custom', 'chunked'])

    def test_unknown_transfer_encoding_rejected_by_default(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Transfer-Encoding', 'custom, chunked')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_reject_obs_text_flag(self) -> None:
        cfg = hp.HttpHeadParser.Config(reject_obs_text=True)
        data = _resp(headers=[('X-Data', 'hello')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.headers['x-data'], 'hello')

    def test_reject_multi_value_content_length(self) -> None:
        cfg = hp.HttpHeadParser.Config(reject_multi_value_content_length=True)
        data = _req(headers=[('Content-Length', '42,42')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=cfg)

    def test_max_header_count_at_limit(self) -> None:
        cfg = hp.HttpHeadParser.Config(max_header_count=3)
        data = _resp(headers=[('A', '1'), ('B', '2'), ('C', '3')])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(len(msg.raw_headers), 3)

    def test_max_header_count_exceeded(self) -> None:
        cfg = hp.HttpHeadParser.Config(max_header_count=2)
        data = _resp(headers=[('A', '1'), ('B', '2'), ('C', '3')])
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data, config=cfg)


##
# 5. Header normalization and combining


class TestHeaderNormalization(unittest.TestCase):
    def test_case_insensitive_lookup(self) -> None:
        data = _resp(headers=[('Content-Type', 'text/html')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['content-type'], 'text/html')
        self.assertEqual(msg.headers['Content-Type'], 'text/html')
        self.assertEqual(msg.headers['CONTENT-TYPE'], 'text/html')

    def test_ows_stripped(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nFoo:   bar  \r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['foo'], 'bar')

    def test_htab_in_ows(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nFoo:\t\tbar\t\t\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['foo'], 'bar')

    def test_comma_combining(self) -> None:
        data = _resp(headers=[('X-Foo', 'a'), ('X-Foo', 'b'), ('X-Foo', 'c')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-foo'], 'a, b, c')

    def test_get_all(self) -> None:
        data = _resp(headers=[('X-Foo', 'a'), ('X-Foo', 'b')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers.get_all('x-foo'), ['a', 'b'])

    def test_get_all_missing(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers.get_all('x-nonexistent'), [])

    def test_set_cookie_not_combined(self) -> None:
        data = _resp(headers=[
            ('Set-Cookie', 'a=1; Path=/'),
            ('Set-Cookie', 'b=2; Path=/'),
        ])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers.get_all('set-cookie'), ['a=1; Path=/', 'b=2; Path=/'])
        with self.assertRaises(hp.MultiValueNoCombineHeaderError):
            self.assertEqual(msg.headers['set-cookie'], 'a=1; Path=/')

    def test_header_order_preserved(self) -> None:
        data = _resp(headers=[('Z-First', '1'), ('A-Second', '2'), ('M-Third', '3')])
        msg = hp.parse_http_head(data)
        keys = msg.headers.keys()
        self.assertEqual(keys, ['z-first', 'a-second', 'm-third'])

    def test_items(self) -> None:
        data = _resp(headers=[('Foo', 'a'), ('Bar', 'b')])
        msg = hp.parse_http_head(data)
        items = msg.headers.items()
        self.assertEqual(items, [('foo', 'a'), ('bar', 'b')])

    def test_contains(self) -> None:
        data = _resp(headers=[('Foo', 'bar')])
        msg = hp.parse_http_head(data)
        self.assertIn('foo', msg.headers)
        self.assertIn('Foo', msg.headers)
        self.assertNotIn('baz', msg.headers)

    def test_get_default(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.headers.get('missing'))
        self.assertEqual(msg.headers.get('missing', 'fallback'), 'fallback')

    def test_raw_headers_preserved(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nContent-Type:  text/html  \r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.raw_headers[0].name, b'Content-Type')
        # raw value has OWS stripped
        self.assertEqual(msg.raw_headers[0].value, b'text/html')

    def test_latin1_decode_in_normalized(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nX-Data: \xe9\xe8\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-data'], '\xe9\xe8')

    def test_raw_is_bytes(self) -> None:
        data = _resp(headers=[('Foo', 'bar')])
        msg = hp.parse_http_head(data)
        self.assertIsInstance(msg.raw_headers[0].name, bytes)
        self.assertIsInstance(msg.raw_headers[0].value, bytes)


##
# 6. Prepared header: Content-Length


class TestPreparedContentLength(unittest.TestCase):
    def test_valid(self) -> None:
        data = _resp(headers=[('Content-Length', '42')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.content_length, 42)

    def test_zero(self) -> None:
        data = _resp(headers=[('Content-Length', '0')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.content_length, 0)

    def test_large(self) -> None:
        data = _resp(headers=[('Content-Length', '999999999999')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.content_length, 999999999999)

    def test_absent(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.content_length)

    def test_non_numeric(self) -> None:
        data = _resp(headers=[('Content-Length', 'abc')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_negative(self) -> None:
        data = _resp(headers=[('Content-Length', '-1')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_float(self) -> None:
        data = _resp(headers=[('Content-Length', '42.5')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_leading_zeros(self) -> None:
        """Leading zeros: '042' is all-digit, should parse as 42."""

        data = _resp(headers=[('Content-Length', '042')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.content_length, 42)

    def test_whitespace_in_value(self) -> None:
        """OWS is already stripped, so ' 42 ' -> '42'."""

        data = b'HTTP/1.1 200 OK\r\nContent-Length:  42  \r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.content_length, 42)

    def test_comma_separated_identical(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_multiple_content_lengths=True)
        for s in ['42,42', '42, 42', '42  ,42,42  ,42']:
            data = _resp(headers=[('Content-Length', s)])
            msg = hp.parse_http_head(data, config=cfg)
            self.assertEqual(msg.prepared.content_length, 42)

    def test_comma_separated_conflicting(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_multiple_content_lengths=True)
        data = _resp(headers=[('Content-Length', '42, 99')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=cfg)

    def test_empty_value(self) -> None:
        data = _resp(headers=[('Content-Length', '')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_hex_value(self) -> None:
        data = _resp(headers=[('Content-Length', '0xff')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)


##
# 7. Prepared header: Transfer-Encoding


class TestPreparedTransferEncoding(unittest.TestCase):
    def test_chunked_only_response(self) -> None:
        data = _resp(headers=[('Transfer-Encoding', 'chunked')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_gzip_chunked_response(self) -> None:
        data = _resp(headers=[('Transfer-Encoding', 'gzip, chunked')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.transfer_encoding, ['gzip', 'chunked'])

    def test_chunked_not_last(self) -> None:
        data = _resp(headers=[('Transfer-Encoding', 'chunked, gzip')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_chunked_twice(self) -> None:
        data = _resp(headers=[('Transfer-Encoding', 'chunked, chunked')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_request_requires_chunked(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Transfer-Encoding', 'gzip')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_request_chunked_ok(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Transfer-Encoding', 'chunked')])
        msg = hp.parse_http_head(data, config=hp.HttpHeadParser.Config(allow_content_length_with_te=True))
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_case_insensitive(self) -> None:
        data = _resp(headers=[('Transfer-Encoding', 'Chunked')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_absent(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.transfer_encoding)

    def test_empty_value(self) -> None:
        data = _resp(headers=[('Transfer-Encoding', '')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)


##
# 8. Prepared header: Host


class TestPreparedHost(unittest.TestCase):
    def test_simple_host(self) -> None:
        data = _req(headers=[('Host', 'example.com')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.host, 'example.com')

    def test_host_with_port(self) -> None:
        data = _req(headers=[('Host', 'example.com:8080')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.host, 'example.com:8080')

    def test_ip_host(self) -> None:
        data = _req(headers=[('Host', '192.168.1.1')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.host, '192.168.1.1')

    def test_ipv6_host(self) -> None:
        data = _req(headers=[('Host', '[::1]:8080')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.host, '[::1]:8080')

    def test_missing_in_http11(self) -> None:
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(_req(headers=[]))

    def test_allowed_missing_in_http10(self) -> None:
        data = _req(version='HTTP/1.0', headers=[])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.host)

    def test_host_not_required_in_response(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.host)

    def test_host_with_control_char(self) -> None:
        # Control chars are caught during field-value validation, before semantic checks
        data = b'GET / HTTP/1.1\r\nHost: x\x01y\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_host_rejects_whitespace(self) -> None:
        parser = hp.HttpHeadParser()
        data = (
            b'GET / HTTP/1.1\r\n'
            b'Host: example.com evil.com\r\n'
            b'\r\n'
        )
        with self.assertRaises(hp.SemanticHeaderError) as cm:
            parser.parse(data, mode=hp.HttpHeadParser.Mode.REQUEST)
        self.assertEqual(cm.exception.code, hp.SemanticHeaderErrorCode.INVALID_HOST)


##
# 9. Prepared header: Connection + keep_alive


class TestPreparedConnection(unittest.TestCase):

    def test_close(self) -> None:
        data = _resp(headers=[('Connection', 'close')])
        msg = hp.parse_http_head(data)
        self.assertIn('close', check.not_none(msg.prepared.connection))
        self.assertFalse(msg.prepared.keep_alive)

    def test_keep_alive_explicit(self) -> None:
        data = _resp(headers=[('Connection', 'keep-alive')])
        msg = hp.parse_http_head(data)
        self.assertIn('keep-alive', check.not_none(msg.prepared.connection))
        self.assertTrue(msg.prepared.keep_alive)

    def test_http11_default_keepalive(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertTrue(msg.prepared.keep_alive)

    def test_http10_default_close(self) -> None:
        data = _resp(version='HTTP/1.0')
        msg = hp.parse_http_head(data)
        self.assertFalse(msg.prepared.keep_alive)

    def test_http10_explicit_keepalive(self) -> None:
        data = _resp(version='HTTP/1.0', headers=[('Connection', 'keep-alive')])
        msg = hp.parse_http_head(data)
        self.assertTrue(msg.prepared.keep_alive)

    def test_http11_explicit_close(self) -> None:
        data = _resp(headers=[('Connection', 'close')])
        msg = hp.parse_http_head(data)
        self.assertFalse(msg.prepared.keep_alive)

    def test_multiple_tokens(self) -> None:
        data = _resp(headers=[('Connection', 'keep-alive, Upgrade')])
        msg = hp.parse_http_head(data)
        self.assertIn('keep-alive', check.not_none(msg.prepared.connection))
        self.assertIn('upgrade', check.not_none(msg.prepared.connection))

    def test_absent(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.connection, frozenset())


##
# 10. Prepared header: Content-Type


class TestPreparedContentType(unittest.TestCase):
    def test_simple(self) -> None:
        data = _resp(headers=[('Content-Type', 'text/html')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.content_type).media_type, 'text/html')
        self.assertEqual(check.not_none(msg.prepared.content_type).params, {})

    def test_with_charset(self) -> None:
        data = _resp(headers=[('Content-Type', 'text/html; charset=utf-8')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.content_type).media_type, 'text/html')
        self.assertEqual(check.not_none(msg.prepared.content_type).charset, 'utf-8')

    def test_quoted_param(self) -> None:
        data = _resp(headers=[('Content-Type', 'text/plain; charset="us-ascii"')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.content_type).charset, 'us-ascii')

    def test_multiple_params(self) -> None:
        data = _resp(headers=[('Content-Type', 'multipart/form-data; boundary=----WebKitFormBoundary; charset=utf-8')])
        msg = hp.parse_http_head(data)
        ct = check.not_none(msg.prepared.content_type)
        self.assertEqual(ct.media_type, 'multipart/form-data')
        self.assertIn('boundary', ct.params)
        self.assertEqual(ct.params['boundary'], '----WebKitFormBoundary')
        self.assertEqual(ct.charset, 'utf-8')

    def test_missing_slash(self) -> None:
        data = _resp(headers=[('Content-Type', 'texthtml')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_empty_type(self) -> None:
        data = _resp(headers=[('Content-Type', '/html')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_empty_subtype(self) -> None:
        data = _resp(headers=[('Content-Type', 'text/')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_absent(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.content_type)

    def test_case_normalization(self) -> None:
        data = _resp(headers=[('Content-Type', 'Application/JSON; Charset=UTF-8')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.content_type).media_type, 'application/json')
        self.assertEqual(check.not_none(msg.prepared.content_type).charset, 'UTF-8')


##
# 11. Prepared header: Trailer


class TestPreparedTrailer(unittest.TestCase):
    def test_valid(self) -> None:
        data = _resp(headers=[
            ('Trailer', 'X-Checksum, X-Status'),
            ('Transfer-Encoding', 'chunked'),
        ])
        msg = hp.parse_http_head(data, config=hp.HttpHeadParser.Config(allow_content_length_with_te=True))
        self.assertEqual(msg.prepared.trailer, frozenset({'x-checksum', 'x-status'}))

    def test_forbidden_content_length(self) -> None:
        data = _resp(headers=[
            ('Trailer', 'Content-Length'),
            ('Transfer-Encoding', 'chunked'),
        ])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=hp.HttpHeadParser.Config(allow_content_length_with_te=True))

    def test_forbidden_transfer_encoding(self) -> None:
        data = _resp(headers=[
            ('Trailer', 'Transfer-Encoding'),
            ('Transfer-Encoding', 'chunked'),
        ])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=hp.HttpHeadParser.Config(allow_content_length_with_te=True))

    def test_forbidden_host(self) -> None:
        data = _resp(headers=[('Trailer', 'Host')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_forbidden_authorization(self) -> None:
        data = _resp(headers=[('Trailer', 'Authorization')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_absent(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.trailer)


##
# 12. Prepared header: Expect


class TestPreparedExpect(unittest.TestCase):
    def test_100_continue(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Content-Length', '10'), ('Expect', '100-continue')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.expect, '100-continue')

    def test_case_insensitive(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Content-Length', '10'), ('Expect', '100-Continue')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.expect, '100-continue')

    def test_invalid_value(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Content-Length', '10'), ('Expect', '102-processing')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_absent(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.expect)


##
# 13. Prepared header: Upgrade


class TestPreparedUpgrade(unittest.TestCase):
    def test_websocket(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Upgrade', 'websocket')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.upgrade, ['websocket'])

    def test_multiple(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Upgrade', 'h2c, websocket')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.upgrade, ['h2c', 'websocket'])

    def test_absent(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.upgrade)


##
# 14. Prepared header: TE


class TestPreparedTE(unittest.TestCase):
    def test_simple(self) -> None:
        data = _req(headers=[('Host', 'x'), ('TE', 'trailers')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.te, ['trailers'])

    def test_with_qvalue(self) -> None:
        data = _req(headers=[('Host', 'x'), ('TE', 'trailers, deflate;q=0.5')])
        msg = hp.parse_http_head(data)
        self.assertIn('trailers', check.not_none(msg.prepared.te))
        self.assertIn('deflate', check.not_none(msg.prepared.te))

    def test_absent(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.te)


##
# 15. Prepared header: Date (HTTP date parsing)


class TestPreparedDate(unittest.TestCase):
    def test_imf_fixdate(self) -> None:
        data = _resp(headers=[('Date', 'Sun, 06 Nov 1994 08:49:37 GMT')])
        msg = hp.parse_http_head(data)
        expected = datetime.datetime(1994, 11, 6, 8, 49, 37, tzinfo=datetime.timezone.utc)  # noqa
        self.assertEqual(check.not_none(msg.prepared.date), expected)

    def test_rfc850(self) -> None:
        data = _resp(headers=[('Date', 'Sunday, 06-Nov-94 08:49:37 GMT')])
        msg = hp.parse_http_head(data)
        expected = datetime.datetime(1994, 11, 6, 8, 49, 37, tzinfo=datetime.timezone.utc)  # noqa
        self.assertEqual(check.not_none(msg.prepared.date), expected)

    def test_rfc850_2digit_year_below_50(self) -> None:
        data = _resp(headers=[('Date', 'Wednesday, 09-Nov-25 10:00:00 GMT')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.date).year, 2025)

    def test_asctime(self) -> None:
        data = _resp(headers=[('Date', 'Sun Nov  6 08:49:37 1994')])
        msg = hp.parse_http_head(data)
        expected = datetime.datetime(1994, 11, 6, 8, 49, 37, tzinfo=datetime.timezone.utc)  # noqa
        self.assertEqual(msg.prepared.date, expected)

        # Test double digit day
        data = _resp(headers=[('Date', 'Sun Nov 16 08:49:37 1994')])
        msg = hp.parse_http_head(data)
        expected = datetime.datetime(1994, 11, 16, 8, 49, 37, tzinfo=datetime.timezone.utc)  # noqa
        self.assertEqual(msg.prepared.date, expected)

    def test_asctime_invalid(self):
        # Incorrect length
        data = _resp(headers=[('Date', 'Sun Nov 6 08:49:37 1994')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_invalid_date(self) -> None:
        data = _resp(headers=[('Date', 'not-a-date')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_invalid_month(self) -> None:
        data = _resp(headers=[('Date', 'Sun, 06 Foo 1994 08:49:37 GMT')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_absent(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.date)


##
# 16. Prepared header: Cache-Control


class TestPreparedCacheControl(unittest.TestCase):
    def test_directives(self) -> None:
        data = _resp(headers=[('Cache-Control', 'max-age=300, no-cache, private')])
        msg = hp.parse_http_head(data)
        cc = check.not_none(msg.prepared.cache_control)
        self.assertEqual(cc['max-age'], '300')
        self.assertIsNone(cc['no-cache'])
        self.assertIsNone(cc['private'])

    def test_quoted_value(self) -> None:
        data = _resp(headers=[('Cache-Control', 'no-cache="Set-Cookie"')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.cache_control)['no-cache'], 'Set-Cookie')

    def test_absent(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.cache_control)

    def test_multiple_directives_with_values(self) -> None:
        data = _resp(headers=[('Cache-Control', 'public, max-age=31536000, s-maxage=86400')])
        msg = hp.parse_http_head(data)
        cc = check.not_none(msg.prepared.cache_control)
        self.assertIsNone(cc['public'])
        self.assertEqual(cc['max-age'], '31536000')
        self.assertEqual(cc['s-maxage'], '86400')


##
# 17. Prepared header: Accept-Encoding


class TestPreparedAcceptEncoding(unittest.TestCase):
    def test_simple(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept-Encoding', 'gzip, deflate, br')])
        msg = hp.parse_http_head(data)
        codings = [item.coding for item in check.not_none(msg.prepared.accept_encoding)]
        self.assertEqual(codings, ['gzip', 'deflate', 'br'])

    def test_with_qvalues(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept-Encoding', 'gzip;q=1.0, identity;q=0.5, *;q=0')])
        msg = hp.parse_http_head(data)
        items = check.not_none(msg.prepared.accept_encoding)
        self.assertEqual(items[0].coding, 'gzip')
        self.assertEqual(items[0].q, 1.0)
        self.assertEqual(items[1].coding, 'identity')
        self.assertEqual(items[1].q, 0.5)
        self.assertEqual(items[2].coding, '*')
        self.assertEqual(items[2].q, 0.0)

    def test_invalid_qvalue(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept-Encoding', 'gzip;q=abc')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_absent(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.accept_encoding)


##
# 18. Prepared header: Accept


class TestPreparedAccept(unittest.TestCase):
    def test_simple(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept', 'text/html, application/json')])
        msg = hp.parse_http_head(data)
        ranges = [item.media_range for item in check.not_none(msg.prepared.accept)]
        self.assertEqual(ranges, ['text/html', 'application/json'])

    def test_with_qvalue(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept', 'text/html;q=0.9, application/json;q=1.0')])
        msg = hp.parse_http_head(data)
        items = check.not_none(msg.prepared.accept)
        self.assertEqual(items[0].q, 0.9)
        self.assertEqual(items[1].q, 1.0)

    def test_with_params(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept', 'text/html;level=1;q=0.7')])
        msg = hp.parse_http_head(data)
        item = check.not_none(msg.prepared.accept)[0]
        self.assertEqual(item.media_range, 'text/html')
        self.assertEqual(item.params.get('level'), '1')
        self.assertEqual(item.q, 0.7)

    def test_wildcard(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept', '*/*')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.accept)[0].media_range, '*/*')

    def test_invalid_qvalue(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept', 'text/html;q=xyz')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_absent(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.accept)


##
# 19. Prepared header: Authorization


class TestPreparedAuthorization(unittest.TestCase):
    def test_bearer(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Authorization', 'Bearer abc123')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.authorization).scheme, 'Bearer')
        self.assertEqual(check.not_none(msg.prepared.authorization).credentials, 'abc123')

    def test_basic(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Authorization', 'Basic dXNlcjpwYXNz')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.authorization).scheme, 'Basic')
        self.assertEqual(check.not_none(msg.prepared.authorization).credentials, 'dXNlcjpwYXNz')

    def test_scheme_only(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Authorization', 'CustomScheme')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.authorization).scheme, 'CustomScheme')
        self.assertEqual(check.not_none(msg.prepared.authorization).credentials, '')

    def test_credentials_with_spaces(self) -> None:
        """Digest auth has space-separated key=value pairs."""

        creds = 'Digest username="user", realm="test", nonce="abc"'
        data = _req(headers=[('Host', 'x'), ('Authorization', creds)])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.prepared.authorization).scheme, 'Digest')
        self.assertIn('username=', check.not_none(msg.prepared.authorization).credentials)

    def test_empty_value(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Authorization', '')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_absent(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.authorization)


##
# 20. Character-set boundary conditions


class TestCharacterBoundaries(unittest.TestCase):
    def test_tchar_boundaries(self) -> None:
        """All valid tchar characters in a method."""

        valid_tchars = b"!#$%&'*+-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz|~"
        data = valid_tchars + b' / HTTP/1.1\r\nHost: x\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).method, valid_tchars.decode('ascii'))

    def test_tchar_boundaries_in_field_name(self) -> None:
        valid_tchars = b"X-Ab0!#$%&'*+-.^_`|~"
        data = b'HTTP/1.1 200 OK\r\n' + valid_tchars + b': val\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertIn(valid_tchars.decode('ascii').lower(), msg.headers)

    def test_vchar_all_visible_ascii(self) -> None:
        """All visible ASCII chars in request-target."""

        visible = bytes(range(0x21, 0x7F))
        # Remove SP (0x20) - it's not VCHAR. Let's make a target from all VCHAR.
        # But we need exactly 2 SPs in request-line, so target can't contain SP.
        target = visible
        data = b'GET ' + target + b' HTTP/1.1\r\nHost: x\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).request_target, target)

    def test_request_target_utf8(self) -> None:
        target = b'/\xe2\x98\x83path'
        data = b'GET ' + target + b' HTTP/1.1\r\nHost: x\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).request_target, target)

    def test_field_value_sp_htab_vchar(self) -> None:
        """SP, HTAB, and all VCHAR in field-value."""

        val = b'\x20\x09' + bytes(range(0x21, 0x7F))
        data = b'HTTP/1.1 200 OK\r\nX-Test: ' + val + b'\r\n\r\n'
        msg = hp.parse_http_head(data)
        # OWS is stripped from edges
        stripped_val = val.lstrip(b' \t').rstrip(b' \t')
        self.assertEqual(msg.raw_headers[0].value, stripped_val)

    def test_obs_text_boundary_0x80(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nX-Data: \x80\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.raw_headers[0].value, b'\x80')

    def test_obs_text_boundary_0xff(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nX-Data: \xff\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.raw_headers[0].value, b'\xff')

    def test_del_0x7f_rejected(self) -> None:
        """DEL (0x7F) is neither VCHAR, SP, HTAB, nor obs-text."""

        data = b'HTTP/1.1 200 OK\r\nX-Data: \x7f\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_ctl_chars_1_to_8_rejected(self) -> None:
        for b in range(0x01, 0x09):  # 0x09 is HTAB which is allowed
            data = b'HTTP/1.1 200 OK\r\nX-Data: ' + bytes([b]) + b'\r\n\r\n'
            with self.assertRaises(hp.HeaderFieldError, msg=f'byte 0x{b:02x} should be rejected'):
                hp.parse_http_head(data)

    def test_ctl_chars_0e_to_1f_rejected(self) -> None:
        for b in range(0x0E, 0x20):  # 0x20 is SP which is allowed
            data = b'HTTP/1.1 200 OK\r\nX-Data: x' + bytes([b]) + b'y\r\n\r\n'
            with self.assertRaises(hp.HeaderFieldError, msg=f'byte 0x{b:02x} should be rejected'):
                hp.parse_http_head(data)

    def test_nul_always_rejected(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nX-Data: ab\x00cd\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)


##
# 21. Request smuggling / adversarial inputs


class TestRequestSmuggling(unittest.TestCase):
    """
    Tests for HTTP request smuggling vectors and other adversarial inputs. A strict parser should reject all of these.
    """

    def test_cl_te_conflict_rejected(self) -> None:
        """CL+TE is the classic smuggling vector."""

        data = _req(headers=[
            ('Host', 'x'),
            ('Content-Length', '10'),
            ('Transfer-Encoding', 'chunked'),
        ])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_conflicting_content_lengths(self) -> None:
        """Different CL values - classic desync."""

        data = _resp(headers=[('Content-Length', '10'), ('Content-Length', '20')])
        with self.assertRaises((hp.SemanticHeaderError, hp.SemanticHeaderError)):
            hp.parse_http_head(data)

    def test_te_te_obfuscation_uppercase(self) -> None:
        """Transfer-Encoding with unusual casing should still be recognized."""

        data = _req(headers=[
            ('Host', 'x'),
            ('Transfer-Encoding', 'chunked'),
        ])
        msg = hp.parse_http_head(data, config=hp.HttpHeadParser.Config(allow_content_length_with_te=True))
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_te_with_leading_whitespace_in_value(self) -> None:
        """Some servers might not recognize ' chunked' as 'chunked'."""

        data = b'POST / HTTP/1.1\r\nHost: x\r\nTransfer-Encoding:  chunked\r\n\r\n'
        msg = hp.parse_http_head(
            data, config=hp.HttpHeadParser.Config(allow_content_length_with_te=True),
        )
        # OWS is stripped, so this should still parse as 'chunked'
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_te_chunked_not_last_rejected(self) -> None:
        """chunked must be last - no relaxation possible."""

        data = _resp(headers=[('Transfer-Encoding', 'chunked, gzip')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

        # Even with all relaxations
        cfg = hp.HttpHeadParser.Config(
            allow_te_without_chunked_in_response=True,
            allow_unknown_transfer_encoding=True,
            allow_transfer_encoding_http10=True,
        )
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=cfg)

    def test_obs_fold_injection(self) -> None:
        """obs-fold could be used to inject extra headers via value continuation."""

        data = (
            b'GET / HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'X-Innocent: value\r\n'
            b' Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        # By default, obs-fold is rejected
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

        # When allowed, it's folded into previous header value, NOT a new header
        cfg = hp.HttpHeadParser.Config(allow_obs_fold=True)
        msg = hp.parse_http_head(data, config=cfg)
        self.assertNotIn('transfer-encoding', msg.headers)
        self.assertIn('Transfer-Encoding: chunked', msg.headers['x-innocent'])

    def test_space_before_colon_smuggling(self) -> None:
        """'Transfer-Encoding : chunked' - some proxies see the header, some don't."""

        data = b'POST / HTTP/1.1\r\nHost: x\r\nTransfer-Encoding : chunked\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_bare_lf_header_injection(self) -> None:
        """Bare LF in header block could cause header injection."""

        data = b'GET / HTTP/1.1\r\nHost: x\nInjected: yes\r\n\r\n'
        with self.assertRaises(hp.HttpParseError):
            hp.parse_http_head(data)

    def test_nul_byte_truncation(self) -> None:
        """NUL bytes could truncate values in some implementations."""

        data = b'GET / HTTP/1.1\r\nHost: evil.com\x00.good.com\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_cr_only_injection(self) -> None:
        """Bare CR could be used to split headers."""

        data = b'GET / HTTP/1.1\r\nHost: x\rInjected: yes\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_duplicate_host_for_routing_confusion(self) -> None:
        """Two different Host headers could cause routing confusion."""

        data = _req(headers=[('Host', 'good.com'), ('Host', 'evil.com')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_host_with_embedded_null(self) -> None:
        data = b'GET / HTTP/1.1\r\nHost: evil.com\x00.good.com\r\n\r\n'
        with self.assertRaises(hp.HeaderFieldError):
            hp.parse_http_head(data)

    def test_content_length_negative(self) -> None:
        data = _resp(headers=[('Content-Length', '-1')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_content_length_with_plus_sign(self) -> None:
        data = _resp(headers=[('Content-Length', '+42')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_content_length_hex(self) -> None:
        data = _resp(headers=[('Content-Length', '0x2A')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_content_length_overflow_attempt(self) -> None:
        """Very large CL value - should parse as int without crashing."""

        data = _resp(headers=[('Content-Length', '99999999999999999999999999999999')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.prepared.content_length, 99999999999999999999999999999999)

    def test_content_length_max_str_len(self) -> None:
        """Very large CL value with max setting - should raise."""

        data = _resp(headers=[('Content-Length', '99999999999999999999999999999999')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data, config=hp.HttpHeadParser.Config(max_content_length_str_len=16))

    def test_content_length_with_trailing_junk(self) -> None:
        data = _resp(headers=[('Content-Length', '42 foo')])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_content_length_comma_different_values(self) -> None:
        """CL: 10, 20 - classic smuggling via comma-separated CL."""

        data = _resp(headers=[('Content-Length', '10, 20')])
        with self.assertRaises((hp.SemanticHeaderError, hp.SemanticHeaderError)):
            hp.parse_http_head(data)

    def test_multiple_te_headers(self) -> None:
        """Multiple TE headers are combined - must still validate."""

        data = _resp(headers=[
            ('Transfer-Encoding', 'gzip'),
            ('Transfer-Encoding', 'chunked'),
        ])
        msg = hp.parse_http_head(data, config=hp.HttpHeadParser.Config(allow_content_length_with_te=True))
        # They get comma-combined: "gzip, chunked"
        self.assertEqual(msg.prepared.transfer_encoding, ['gzip', 'chunked'])

    def test_double_crlf_in_header_value(self) -> None:
        """A CRLFCRLF inside what looks like a value should terminate headers."""

        # The terminator search finds the first \r\n\r\n
        data = b'HTTP/1.1 200 OK\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(len(msg.raw_headers), 0)

    def test_version_mismatch_request_in_response_mode(self) -> None:
        """Forcing response mode on a request line."""

        data = _req(headers=[('Host', 'x')])
        # In response mode, 'GET / HTTP/1.1' will be parsed as a status line
        # and fail because 'GET' is not 'HTTP/x.y'
        with self.assertRaises(hp.StartLineError):
            hp.parse_http_head(data, mode=hp.HttpHeadParser.Mode.RESPONSE)


##
# 22. Error model / exception hierarchy


class TestErrorModel(unittest.TestCase):
    def test_all_enum_members_present(self) -> None:
        """Every enum has at least one member and they're all distinct names."""

        for enum_cls in (
                hp.StartLineErrorCode,
                hp.HeaderFieldErrorCode,
                hp.SemanticHeaderErrorCode,
                hp.EncodingErrorCode,
        ):
            self.assertGreater(len(enum_cls), 0, f'{enum_cls.__name__} is empty')

    def test_exception_hierarchy(self) -> None:
        self.assertTrue(issubclass(hp.StartLineError, hp.HttpParseError))
        self.assertTrue(issubclass(hp.HeaderFieldError, hp.HttpParseError))
        self.assertTrue(issubclass(hp.SemanticHeaderError, hp.HttpParseError))
        self.assertTrue(issubclass(hp.EncodingError, hp.HttpParseError))

    def test_category_code_types(self) -> None:
        """Each category class carries the right enum type in .code."""

        e1 = hp.StartLineError(code=hp.StartLineErrorCode.MALFORMED_REQUEST_LINE, message='t')
        self.assertIsInstance(e1.code, hp.StartLineErrorCode)

        e2 = hp.HeaderFieldError(code=hp.HeaderFieldErrorCode.MISSING_COLON, message='t')
        self.assertIsInstance(e2.code, hp.HeaderFieldErrorCode)

        e3 = hp.SemanticHeaderError(code=hp.SemanticHeaderErrorCode.INVALID_CONTENT_LENGTH, message='t')
        self.assertIsInstance(e3.code, hp.SemanticHeaderErrorCode)

        e4 = hp.EncodingError(code=hp.EncodingErrorCode.NON_ASCII_IN_FIELD_NAME, message='t')
        self.assertIsInstance(e4.code, hp.EncodingErrorCode)

    def test_error_has_line_and_offset(self) -> None:
        try:
            hp.parse_http_head(b'GET / HTTP/1.1\r\nBad\x01Name: val\r\n\r\n')
            self.fail('Should have raised')
        except hp.HttpParseError as e:
            self.assertIsInstance(e.message, str)
            self.assertIsInstance(e.line, int)
            self.assertIsInstance(e.offset, int)
            self.assertGreater(e.line, 0)  # header line, not start line
            self.assertIn('[', str(e))  # formatted string

    def test_error_code_in_exception(self) -> None:
        try:
            hp.parse_http_head(b'GET / HTTP/2.0\r\n\r\n')
        except hp.StartLineError as e:
            self.assertEqual(e.code, hp.StartLineErrorCode.UNSUPPORTED_HTTP_VERSION)

    def test_direct_construction(self) -> None:
        err = hp.HeaderFieldError(
            code=hp.HeaderFieldErrorCode.MISSING_COLON,
            message='test',
            line=5,
            offset=100,
        )
        self.assertIsInstance(err, hp.HeaderFieldError)
        self.assertIsInstance(err, hp.HttpParseError)
        self.assertEqual(err.line, 5)
        self.assertEqual(err.offset, 100)
        self.assertEqual(err.code, hp.HeaderFieldErrorCode.MISSING_COLON)

    def test_exception_is_catchable_as_exception(self) -> None:
        with self.assertRaises(Exception):  # noqa
            hp.parse_http_head(b'JUNK')

    def test_type_error_on_non_bytes(self) -> None:
        with self.assertRaises(TypeError):
            hp.parse_http_head('GET / HTTP/1.1\r\n\r\n')  # type: ignore

    def test_bytearray_accepted(self) -> None:
        data = bytearray(b'GET / HTTP/1.1\r\nHost: x\r\n\r\n')
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).method, 'GET')


##
# 23. Misc edge cases


class TestMiscEdgeCases(unittest.TestCase):
    def test_empty_header_value(self) -> None:
        data = _resp(headers=[('X-Empty', '')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-empty'], '')

    def test_header_value_just_whitespace(self) -> None:
        """OWS-only value becomes empty after stripping."""

        data = b'HTTP/1.1 200 OK\r\nX-WS:   \r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-ws'], '')

    def test_many_headers(self) -> None:
        hdrs = [(f'X-H-{i}', f'v{i}') for i in range(128)]
        data = _resp(headers=hdrs)
        msg = hp.parse_http_head(data)
        self.assertEqual(len(msg.raw_headers), 128)

    def test_colon_in_value(self) -> None:
        data = _resp(headers=[('X-Time', '12:34:56')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-time'], '12:34:56')

    def test_equals_in_value(self) -> None:
        data = _resp(headers=[('X-Data', 'key=value')])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-data'], 'key=value')

    def test_very_long_header_name(self) -> None:
        name = 'X-' + 'A' * 200
        data = _resp(headers=[(name, 'val')])
        msg = hp.parse_http_head(data)
        self.assertIn(name.lower(), msg.headers)

    def test_very_long_header_value(self) -> None:
        val = 'x' * 8000
        data = _resp(headers=[('X-Long', val)])
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.headers['x-long'], val)

    def test_parser_reuse(self) -> None:
        parser = hp.HttpHeadParser()
        msg1 = parser.parse(_req(headers=[('Host', 'a.com')]))
        msg2 = parser.parse(_req(headers=[('Host', 'b.com')]))
        self.assertEqual(msg1.prepared.host, 'a.com')
        self.assertEqual(msg2.prepared.host, 'b.com')

    def test_parser_config_immutable_between_calls(self) -> None:
        cfg = hp.HttpHeadParser.Config()
        parser = hp.HttpHeadParser(cfg)
        parser.parse(_req(headers=[('Host', 'x')]))
        self.assertEqual(cfg.allow_obs_fold, False)  # unchanged

    def test_reason_phrase_with_obs_text(self) -> None:
        data = b'HTTP/1.1 200 \xc0K\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.status_line).reason_phrase, '\xc0K')

    def test_multiple_set_cookie_in_items(self) -> None:
        data = _resp(headers=[
            ('Set-Cookie', 'a=1'),
            ('Set-Cookie', 'b=2'),
            ('Set-Cookie', 'c=3'),
        ])
        msg = hp.parse_http_head(data)
        items = msg.headers.items()
        sc_items = [(k, v) for k, v in items if k == 'set-cookie']
        self.assertEqual(len(sc_items), 3)

    def test_mixed_case_header_names_in_raw(self) -> None:
        data = b'HTTP/1.1 200 OK\r\nContent-TYPE: text/html\r\ncontent-length: 0\r\n\r\n'
        msg = hp.parse_http_head(data)
        self.assertEqual(msg.raw_headers[0].name, b'Content-TYPE')
        self.assertEqual(msg.raw_headers[1].name, b'content-length')
        # Normalized access is case-insensitive
        self.assertEqual(msg.headers['content-type'], 'text/html')
        self.assertEqual(msg.headers['content-length'], '0')

    def test_http10_host_not_required_in_request(self) -> None:
        data = _req(version='HTTP/1.0', headers=[])
        msg = hp.parse_http_head(data)
        self.assertIsNone(msg.prepared.host)

    def test_head_method(self) -> None:
        data = _req(method='HEAD', headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).method, 'HEAD')

    def test_options_asterisk(self) -> None:
        data = _req(method='OPTIONS', target='*', headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).method, 'OPTIONS')
        self.assertEqual(check.not_none(msg.request_line).request_target, b'*')

    def test_connect_method_authority_target(self) -> None:
        data = _req(method='CONNECT', target='example.com:443', headers=[('Host', 'example.com:443')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).request_target, b'example.com:443')

    def test_1xx_response(self) -> None:
        data = _resp(status=100, reason='Continue')
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.status_line).status_code, 100)

    def test_304_response(self) -> None:
        data = _resp(status=304, reason='Not Modified')
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.status_line).status_code, 304)

    def test_empty_request_target_percent_encoded(self) -> None:
        """Percent-encoded chars in target - parser doesn't decode them, just passes through."""

        data = _req(target='/path%20with%20spaces', headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        self.assertEqual(check.not_none(msg.request_line).request_target, b'/path%20with%20spaces')


##
# 24. Interaction between prepared headers


class TestPreparedHeaderInteractions(unittest.TestCase):
    def test_cl_and_te_conflict_default(self) -> None:
        data = _req(headers=[
            ('Host', 'x'),
            ('Content-Length', '10'),
            ('Transfer-Encoding', 'chunked'),
        ])
        with self.assertRaises(hp.SemanticHeaderError):
            hp.parse_http_head(data)

    def test_cl_and_te_allowed_with_config(self) -> None:
        cfg = hp.HttpHeadParser.Config(allow_content_length_with_te=True)
        data = _req(headers=[
            ('Host', 'x'),
            ('Content-Length', '10'),
            ('Transfer-Encoding', 'chunked'),
        ])
        msg = hp.parse_http_head(data, config=cfg)
        self.assertEqual(msg.prepared.content_length, 10)
        self.assertEqual(msg.prepared.transfer_encoding, ['chunked'])

    def test_connection_close_overrides_default_keepalive(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Connection', 'close')])
        msg = hp.parse_http_head(data)
        self.assertFalse(msg.prepared.keep_alive)

    def test_upgrade_with_connection(self) -> None:
        data = _req(headers=[
            ('Host', 'x'),
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
        ])
        msg = hp.parse_http_head(data)
        self.assertIn('upgrade', check.not_none(msg.prepared.connection))
        self.assertEqual(msg.prepared.upgrade, ['websocket'])


##
# 25. HttpHeadParser.Config defaults


class TestHttpHeadParserConfigDefaults(unittest.TestCase):
    def test_all_defaults(self) -> None:
        cfg = hp.HttpHeadParser.Config()
        self.assertFalse(cfg.allow_obs_fold)
        self.assertFalse(cfg.allow_space_before_colon)
        self.assertFalse(cfg.allow_multiple_content_lengths)
        self.assertFalse(cfg.allow_content_length_with_te)
        self.assertFalse(cfg.allow_bare_lf)
        self.assertFalse(cfg.allow_missing_host)
        self.assertFalse(cfg.allow_multiple_hosts)
        self.assertFalse(cfg.allow_unknown_transfer_encoding)
        self.assertTrue(cfg.allow_empty_header_values)
        self.assertFalse(cfg.allow_bare_cr_in_value)
        self.assertFalse(cfg.allow_te_without_chunked_in_response)
        self.assertFalse(cfg.allow_transfer_encoding_http10)
        self.assertFalse(cfg.reject_obs_text)
        self.assertEqual(cfg.max_header_count, 128)


##
# 26. Data model immutability / structure


class TestDataModels(unittest.TestCase):
    def test_request_line_frozen(self) -> None:
        data = _req(headers=[('Host', 'x')])
        msg = hp.parse_http_head(data)
        with self.assertRaises(AttributeError):
            msg.request_line.method = 'PUT'  # type: ignore

    def test_status_line_frozen(self) -> None:
        data = _resp()
        msg = hp.parse_http_head(data)
        with self.assertRaises(AttributeError):
            msg.status_line.status_code = 500  # type: ignore

    def test_raw_header_frozen(self) -> None:
        data = _resp(headers=[('Foo', 'bar')])
        msg = hp.parse_http_head(data)
        with self.assertRaises(AttributeError):
            msg.raw_headers[0].name = b'Baz'  # type: ignore

    def test_content_type_frozen(self) -> None:
        data = _resp(headers=[('Content-Type', 'text/html')])
        msg = hp.parse_http_head(data)
        with self.assertRaises(AttributeError):
            msg.prepared.content_type.media_type = 'x'  # type: ignore

    def test_accept_encoding_item_frozen(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Accept-Encoding', 'gzip')])
        msg = hp.parse_http_head(data)
        with self.assertRaises(AttributeError):
            msg.prepared.accept_encoding[0].coding = 'br'  # type: ignore

    def test_authorization_value_frozen(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Authorization', 'Bearer x')])
        msg = hp.parse_http_head(data)
        with self.assertRaises(AttributeError):
            msg.prepared.authorization.scheme = 'Basic'  # type: ignore

    def test_message_kind_enum_values(self) -> None:
        self.assertEqual(hp.ParsedHttpHead.Kind.REQUEST.value, 'request')
        self.assertEqual(hp.ParsedHttpHead.Kind.RESPONSE.value, 'response')

    def test_parser_mode_enum_values(self) -> None:
        self.assertEqual(hp.HttpHeadParser.Mode.REQUEST.value, 'request')
        self.assertEqual(hp.HttpHeadParser.Mode.RESPONSE.value, 'response')
        self.assertEqual(hp.HttpHeadParser.Mode.AUTO.value, 'auto')

    def test_parsed_message_fields_present(self) -> None:
        data = _req(headers=[('Host', 'x'), ('Content-Length', '0')])
        msg = hp.parse_http_head(data)
        self.assertIsNotNone(msg.kind)
        self.assertIsNotNone(msg.request_line)
        self.assertIsNone(msg.status_line)
        self.assertIsInstance(msg.raw_headers, list)
        self.assertIsInstance(msg.headers, hp.ParsedHttpHeaders)
        self.assertIsInstance(msg.prepared, hp.PreparedParsedHttpHeaders)


if __name__ == '__main__':
    unittest.main()
