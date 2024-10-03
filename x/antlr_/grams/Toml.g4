/*
https://github.com/antlr/grammars-v4/blob/f9b1c203dc6368d972bedcb6f8c3670688ad8008/toml/toml.g4
*/
grammar Toml;


document
    : expression (NL expression)*
    ;

expression
    : keyValue comment
    | table comment
    | comment
    ;

comment
    : COMMENT?
    ;

keyValue
    : key '=' value
    ;

key
    : simpleKey
    | dottedKey
    ;

simpleKey
    : quotedKey
    | unquotedKey
    ;

unquotedKey
    : UNQUOTED_KEY
    ;

quotedKey
    : BASIC_STRING
    | LITERAL_STRING
    ;

dottedKey
    : simpleKey ('.' simpleKey)+
    ;

value
    : string
    | integer
    | floatingPoint
    | boolean
    | dateTime
    | array
    | inlineTable
    ;

string
    : BASIC_STRING
    | ML_BASIC_STRING
    | LITERAL_STRING
    | ML_LITERAL_STRING
    ;

integer
    : DEC_INT
    | HEX_INT
    | OCT_INT
    | BIN_INT
    ;

floatingPoint
    : FLOAT
    | INF
    | NAN
    ;

boolean
    : BOOLEAN
    ;

dateTime
    : OFFSET_DATE_TIME
    | LOCAL_DATE_TIME
    | LOCAL_DATE
    | LOCAL_TIME
    ;

array
    : '[' arrayValues? commentOrNl ']'
    ;

arrayValues
    : (commentOrNl value ',' arrayValues commentOrNl)
    | commentOrNl value ','?
    ;

commentOrNl
    : (COMMENT? NL)*
    ;

table
    : standardTable
    | arrayTable
    ;

standardTable
    : '[' key ']'
    ;

inlineTable
    : '{' inlineTableKeyvals '}'
    ;

inlineTableKeyvals
    : inlineTableKeyvalsNonEmpty?
    ;

inlineTableKeyvalsNonEmpty
    : key '=' value (',' inlineTableKeyvalsNonEmpty)?
    ;

arrayTable
    : '[[' key ']]'
    ;

WS
    : [ \t]+ -> skip
    ;

NL
    : ('\r'? '\n')+
    ;

COMMENT
    : '#' (~[\n])*
    ;

fragment DIGIT
    : [0-9]
    ;

fragment ALPHA
    : [A-Za-z]
    ;

BOOLEAN
    : 'true'
    | 'false'
    ;

fragment ESC
    : '\\' (["\\/bfnrt] | UNICODE | EX_UNICODE)
    ;

fragment ML_ESC
    : '\\' '\r'? '\n'
    | ESC
    ;

fragment UNICODE
    : 'u' HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT
    ;

fragment EX_UNICODE
    : 'U' HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT
    ;

BASIC_STRING
    : '"' (ESC | ~["\\\n])*? '"'
    ;

ML_BASIC_STRING
    : '"""' (ML_ESC | ~["\\])*? '"""'
    ;

LITERAL_STRING
    : '\'' (~['\n])*? '\''
    ;

ML_LITERAL_STRING
    : '\'\'\'' (.)*? '\'\'\''
    ;

fragment EXP
    : ('e' | 'E') DEC_INT
    ;

fragment ZERO_PREFIXABLE_INT
    : DIGIT (DIGIT | '_' DIGIT)*
    ;

fragment FRAC
    : '.' ZERO_PREFIXABLE_INT
    ;

FLOAT
    : DEC_INT (EXP | FRAC EXP?)
    ;

INF
    : [+-]? 'inf'
    ;

NAN
    : [+-]? 'nan'
    ;

fragment HEX_DIGIT
    : [A-F]
    | DIGIT
    ;

fragment DIGIT_1_9
    : [1-9]
    ;

fragment DIGIT_0_7
    : [0-7]
    ;

fragment DIGIT_0_1
    : [0-1]
    ;

DEC_INT
    : [+-]? (DIGIT | (DIGIT_1_9 (DIGIT | '_' DIGIT)+))
    ;

HEX_INT
    : '0x' HEX_DIGIT (HEX_DIGIT | '_' HEX_DIGIT)*
    ;

OCT_INT
    : '0o' DIGIT_0_7 (DIGIT_0_7 | '_' DIGIT_0_7)
    ;

BIN_INT
    : '0b' DIGIT_0_1 (DIGIT_0_1 | '_' DIGIT_0_1)*
    ;

fragment YEAR
    : DIGIT DIGIT DIGIT DIGIT
    ;

fragment MONTH
    : DIGIT DIGIT
    ;

fragment DAY
    : DIGIT DIGIT
    ;

fragment DELIM
    : 'T'
    | 't'
    ;

fragment HOUR
    : DIGIT DIGIT
    ;

fragment MINUTE
    : DIGIT DIGIT
    ;

fragment SECOND
    : DIGIT DIGIT
    ;

fragment SECFRAC
    : '.' DIGIT+
    ;

fragment NUMOFFSET
    : ('+' | '-') HOUR ':' MINUTE
    ;

fragment OFFSET
    : 'Z'
    | NUMOFFSET
    ;

fragment PARTIAL_TIME
    : HOUR ':' MINUTE ':' SECOND SECFRAC?
    ;

fragment FULL_DATE
    : YEAR '-' MONTH '-' DAY
    ;

fragment FULL_TIME
    : PARTIAL_TIME OFFSET
    ;

OFFSET_DATE_TIME
    : FULL_DATE DELIM FULL_TIME
    ;

LOCAL_DATE_TIME
    : FULL_DATE DELIM PARTIAL_TIME
    ;

LOCAL_DATE
    : FULL_DATE
    ;

LOCAL_TIME
    : PARTIAL_TIME
    ;

UNQUOTED_KEY
    : (ALPHA | DIGIT | '-' | '_')+
    ;
