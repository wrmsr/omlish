/*
https://www.python.org/dev/peps/pep-0508/#grammar

https://www.python.org/dev/peps/pep-0345/ Python distribution metadata version 1.2.
https://www.python.org/dev/peps/pep-0426/ Python distribution metadata.
https://www.python.org/dev/peps/pep-0440/ Python distribution metadata.
https://tools.ietf.org/html/rfc3986 The URL specification.


wsp           = ' ' | '\t'
version_cmp   = wsp* <'<=' | '<' | '!=' | '==' | '>=' | '>' | '~=' | '==='>
version       = wsp* <( letterOrDigit | '-' | '_' | '.' | '*' | '+' | '!' )+>
version_one   = version_cmp:op version:v wsp* -> (op, v)
version_many  = version_one:v1 (wsp* ',' version_one)*:v2 -> [v1] + v2
versionspec   = ('(' version_many:v ')' ->v) | version_many
urlspec       = '@' wsp* <URI_reference>
marker_op     = version_cmp | (wsp* 'in') | (wsp* 'not' wsp+ 'in')
python_str_c  = (wsp | letter | digit | '(' | ')' | '.' | '{' | '}' |
                 '-' | '_' | '*' | '#' | ':' | ';' | ',' | '/' | '?' |
                 '[' | ']' | '!' | '~' | '`' | '@' | '$' | '%' | '^' |
                 '&' | '=' | '+' | '|' | '<' | '>' )
dquote        = '"'
squote        = '\\''
python_str    = (squote <(python_str_c | dquote)*>:s squote |
                 dquote <(python_str_c | squote)*>:s dquote) -> s
env_var       = ('python_version' | 'python_full_version' |
                 'os_name' | 'sys_platform' | 'platform_release' |
                 'platform_system' | 'platform_version' |
                 'platform_machine' | 'platform_python_implementation' |
                 'implementation_name' | 'implementation_version' |
                 'extra' # ONLY when defined by a containing layer
                 ):varname -> lookup(varname)
marker_var    = wsp* (env_var | python_str)
marker_expr   = marker_var:l marker_op:o marker_var:r -> (o, l, r)
              | wsp* '(' marker:m wsp* ')' -> m
marker_and    = marker_expr:l wsp* 'and' marker_expr:r -> ('and', l, r)
              | marker_expr:m -> m
marker_or     = marker_and:l wsp* 'or' marker_and:r -> ('or', l, r)
                  | marker_and:m -> m
marker        = marker_or
quoted_marker = ';' wsp* marker
identifier_end = letterOrDigit | (('-' | '_' | '.' )* letterOrDigit)
identifier    = < letterOrDigit identifier_end* >
name          = identifier
extras_list   = identifier:i (wsp* ',' wsp* identifier)*:ids -> [i] + ids
extras        = '[' wsp* extras_list?:e wsp* ']' -> e
name_req      = (name:n wsp* extras?:e wsp* versionspec?:v wsp* quoted_marker?:m
                 -> (n, e or [], v or [], m))
url_req       = (name:n wsp* extras?:e wsp* urlspec:v (wsp+ | end) quoted_marker?:m
                 -> (n, e or [], v, m))
specification = wsp* ( url_req | name_req ):s wsp* -> s
# The result is a tuple - name, list-of-extras,
# list-of-version-constraints-or-a-url, marker-ast or None

URI_reference = <URI | relative_ref>
URI           = scheme ':' hier_part ('?' query )? ( '#' fragment)?
hier_part     = ('//' authority path_abempty) | path_absolute | path_rootless | path_empty
absolute_URI  = scheme ':' hier_part ( '?' query )?
relative_ref  = relative_part ( '?' query )? ( '#' fragment )?
relative_part = '//' authority path_abempty | path_absolute | path_noscheme | path_empty
scheme        = letter ( letter | digit | '+' | '-' | '.')*
authority     = ( userinfo '@' )? host ( ':' port )?
userinfo      = ( unreserved | pct_encoded | sub_delims | ':')*
host          = IP_literal | IPv4address | reg_name
port          = digit*
IP_literal    = '[' ( IPv6address | IPvFuture) ']'
IPvFuture     = 'v' hexdig+ '.' ( unreserved | sub_delims | ':')+
IPv6address   = (
                  ( h16 ':'){6} ls32
                  | '::' ( h16 ':'){5} ls32
                  | ( h16 )?  '::' ( h16 ':'){4} ls32
                  | ( ( h16 ':')? h16 )? '::' ( h16 ':'){3} ls32
                  | ( ( h16 ':'){0,2} h16 )? '::' ( h16 ':'){2} ls32
                  | ( ( h16 ':'){0,3} h16 )? '::' h16 ':' ls32
                  | ( ( h16 ':'){0,4} h16 )? '::' ls32
                  | ( ( h16 ':'){0,5} h16 )? '::' h16
                  | ( ( h16 ':'){0,6} h16 )? '::' )
h16           = hexdig{1,4}
ls32          = ( h16 ':' h16) | IPv4address
IPv4address   = dec_octet '.' dec_octet '.' dec_octet '.' dec_octet
nz            = ~'0' digit
dec_octet     = (
                  digit # 0-9
                  | nz digit # 10-99
                  | '1' digit{2} # 100-199
                  | '2' ('0' | '1' | '2' | '3' | '4') digit # 200-249
                  | '25' ('0' | '1' | '2' | '3' | '4' | '5') )# %250-255
reg_name = ( unreserved | pct_encoded | sub_delims)*
path = (
        path_abempty # begins with '/' or is empty
        | path_absolute # begins with '/' but not '//'
        | path_noscheme # begins with a non-colon segment
        | path_rootless # begins with a segment
        | path_empty ) # zero characters
path_abempty  = ( '/' segment)*
path_absolute = '/' ( segment_nz ( '/' segment)* )?
path_noscheme = segment_nz_nc ( '/' segment)*
path_rootless = segment_nz ( '/' segment)*
path_empty    = pchar{0}
segment       = pchar*
segment_nz    = pchar+
segment_nz_nc = ( unreserved | pct_encoded | sub_delims | '@')+
                # non-zero-length segment without any colon ':'
pchar         = unreserved | pct_encoded | sub_delims | ':' | '@'
query         = ( pchar | '/' | '?')*
fragment      = ( pchar | '/' | '?')*
pct_encoded   = '%' hexdig
unreserved    = letter | digit | '-' | '.' | '_' | '~'
reserved      = gen_delims | sub_delims
gen_delims    = ':' | '/' | '?' | '#' | '(' | ')?' | '@'
sub_delims    = '!' | '$' | '&' | '\\'' | '(' | ')' | '*' | '+' | ',' | ';' | '='
hexdig        = digit | 'a' | 'A' | 'b' | 'B' | 'c' | 'C' | 'd' | 'D' | 'e' | 'E' | 'f' | 'F'
*/
grammar Pep508;


oneSpec
    : spec EOF
    ;

spec
    : nameReq
//    | urlReq
    ;

nameReq
    : name extras? versionspec? quotedMarker?
    ;

name
    : identifier
    ;

identifier
    : LETTERS_OR_DIGITS (('-' | '_' | '.') | LETTERS_OR_DIGITS)*
    ;

extras
    : '[' extrasList? ']'
    ;

extrasList
    : identifier (',' identifier)*
    ;

versionspec
    : '(' versionMany ')'
    | versionMany
    ;

versionMany
    : versionOne (',' versionOne)*
    ;

versionOne
    : versionCmp version
    ;

versionCmp
    : '<='
    | '<'
    | '!='
    | '=='
    | '>='
    | '>'
    | '~='
    | '==='
    ;

version
    : (LETTERS_OR_DIGITS | '-' | '_' | '.' | '*' | '+' | '!')+
    ;

quotedMarker
    : ';' marker
    ;

marker
    : markerOr
    ;

markerOr
    : markerAnd OR markerAnd
    | markerAnd
    ;

markerAnd
    : markerExpr AND markerExpr
    | markerExpr
    ;

markerExpr
    : markerVar markerOp markerVar
    | '(' marker ')'
    ;

markerVar
    : envVar
    | pythonStr
    ;

markerOp
    : versionCmp
    | IN
    | (NOT IN)
    ;

envVar
    : 'python_version'
    | 'python_full_version'
    | 'os_name'
    | 'sys_platform'
    | 'platform_release'
    | 'platform_system'
    | 'platform_version'
    | 'platform_machine'
    | 'platform_python_implementation'
    | 'implementation_name'
    | 'implementation_version'
    | EXTRA  // ONLY when defined by a containing layer
    ;

pythonStr
    : SQUOTE (~DQUOTE)* SQUOTE
    | DQUOTE (~SQUOTE)* DQUOTE
    ;

pythonChar
    : LETTER_OR_DIGIT+
    | '('
    | ')'
    | '.'
    | '{'
    | '}'
    | '-'
    | '_'
    | '*'
    | '#'
    | ':'
    | ';'
    | ','
    | '/'
    | '?'
    | '['
    | ']'
    | '!'
    | '~'
    | '`'
    | '@'
    | '$'
    | '%'
    | '^'
    | '&'
    | '='
    | '+'
    | '|'
    | '<'
    | '>'
    ;

//urlReq
//    : name extras? urlspec quotedMarker?
//    ;

//urlspec
//    : '@' uriReference
//    ;

//uriReference
//    : URI_CHAR+
//    ;

//uriChar
//    : LETTER_OR_DIGIT+
//    |

AND: 'and';
EXTRA: 'extra';
IN: 'in';
NOT: 'not';
OR: 'or';

LETTERS_OR_DIGITS
    : LETTER_OR_DIGIT+
    | AND
    | EXTRA
    | IN
    | NOT
    | OR
    ;

LETTER_OR_DIGIT
    : [A-Za-z0-9]
    ;

SQUOTE
    : '\''
    ;

DQUOTE
    : '"'
    ;

COMMENT
    : '#' ~[\r\n]* '\r'? '\n'? -> channel(HIDDEN)
    ;

WS
    : [ \t\n\r]+ -> skip
    ;
