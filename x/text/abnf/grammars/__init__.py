"""Grammars extracted from various RFC."""
"""
RFC 2616 – Hypertext Transfer Protocol -- HTTP/1.1
Defines the HTTP/1.1 protocol, including methods (GET, POST, etc.), status codes, headers, and caching. It was the
foundational HTTP spec but is now obsolete, replaced by RFCs 7230–7235 and later 9110–9111.

RFC 3339 – Date and Time on the Internet: Timestamps
Specifies a profile of ISO 8601 for use in Internet protocols, focusing on a standard format for timestamps (e.g.,
2025-05-12T13:45:30Z), ensuring consistency and interoperability.

RFC 3629 – UTF-8, a transformation format of ISO 10646
Specifies UTF-8 encoding for Unicode, allowing characters from nearly all human languages to be represented in a
backward-compatible way with ASCII.

RFC 3986 – Uniform Resource Identifier (URI): Generic Syntax
Defines the syntax of URIs, breaking them into scheme, authority, path, query, and fragment components. It’s the basis
for most modern web addressing.

RFC 3987 – Internationalized Resource Identifiers (IRIs)
Extends URIs to support non-ASCII characters using Unicode, enabling links and identifiers in native languages.

RFC 4647 – Matching of Language Tags
Describes how to match language tags (like en-US, fr-CA) for purposes like content negotiation or UI localization.

RFC 5234 – Augmented BNF for Syntax Specifications: ABNF
Describes the ABNF notation used in many IETF protocols to define grammars and syntax rules. It replaces RFC 2234.

RFC 5322 – Internet Message Format
Defines the syntax for email messages, including headers (like From, To, Subject) and message bodies. Updates and
obsoletes RFC 2822.

RFC 5646 – Tags for Identifying Languages
Defines the structure and use of language tags (e.g., en-US, zh-Hant-TW) to indicate content language, building on RFC
4646 and BCP 47.

RFC 5987 – Character Set and Language Encoding for HTTP Header Field Parameters
Introduces a way to encode non-ASCII characters in HTTP headers (e.g., filenames in Content-Disposition) using percent
encoding and character sets.

RFC 6265 – HTTP State Management Mechanism (Cookies)
Specifies how cookies work in HTTP for maintaining session state between client and server. It clarifies security and
behavior across browsers.

RFC 6266 – Use of the Content-Disposition Header Field in the HTTP
Defines the use of the Content-Disposition header in HTTP responses, such as indicating attachment filenames for file
downloads.

RFC 7230 – HTTP/1.1: Message Syntax and Routing
Part of the HTTP/1.1 revision. Defines how HTTP messages are structured and routed between clients and servers.
Supersedes parts of RFC 2616.

RFC 7231 – HTTP/1.1: Semantics and Content
Specifies HTTP request methods, status codes, headers, and the semantics of how HTTP works. Complements RFC 7230.

RFC 7232 – HTTP/1.1: Conditional Requests
Details conditional request headers (like If-Modified-Since, If-None-Match) used to optimize network usage and cache
validation.

RFC 7233 – HTTP/1.1: Range Requests
Defines how clients can request partial resources (e.g., bytes 100–200 of a file), allowing resumable downloads and
media streaming.

RFC 7234 – HTTP/1.1: Caching
Describes caching behavior and control in HTTP using headers like Cache-Control, Expires, and ETag.

RFC 7235 – HTTP/1.1: Authentication
Specifies HTTP authentication mechanisms (like Basic and Digest) using the Authorization and WWW-Authenticate headers.

RFC 7405 – ABNF Extensions for Case Sensitivity
Adds syntax to ABNF allowing case-sensitive string literals (via %s"..."), improving clarity in protocol specifications.

RFC 7489 – Domain-based Message Authentication, Reporting, and Conformance (DMARC)
Defines DMARC, an email authentication protocol that helps protect domains from spoofing by combining SPF and DKIM
results.

RFC 8187 – Character Encoding for HTTP Header Field Parameters
Updates RFC 5987 by refining the syntax and usage of non-ASCII parameter values in HTTP headers, like filename*=.

RFC 9110 – HTTP Semantics
Part of the HTTP/1.1 and HTTP/2 refresh, it consolidates and updates the semantics portion of HTTP (methods, headers,
status codes). Supersedes RFCs 7231, 7232, 7233, 7235.

RFC 9111 – HTTP Caching
Updates and consolidates HTTP caching rules, superseding RFC 7234. Addresses how and when responses are stored and
reused.

RFC 9116 – A File Format to Aid in Security Vulnerability Disclosure
Specifies the security.txt file format for websites to declare security contact information, allowing researchers to
report vulnerabilities responsibly.
"""
