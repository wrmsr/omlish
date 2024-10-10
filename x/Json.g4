/*
https://github.com/antlr/grammars-v4/blob/f9b1c203dc6368d972bedcb6f8c3670688ad8008/json/JSON.g4

Taken from "The Definitive ANTLR 4 Reference" by Terence Parr.

Derived from http://json.org
*/
grammar Json;


json
    : value
    ;

obj
    : '{' pair (',' pair)* '}'
    | '{' '}'
    ;

pair
    : key ':' value
    ;

key
    : STRING
    ;

array
    : '[' value (',' value)* ']'
    | '[' ']'
    ;

value
    : STRING
    | NUMBER
    | obj
    | array
    | TRUE
    | FALSE
    | NULL
    ;

STRING
    : '"' (ESC | SAFE_CODEPOINT)* '"'
    ;

fragment ESC
    : '\\' (["\\/bfnrt] | UNICODE)
    ;

fragment UNICODE
    : 'u' HEX HEX HEX HEX
    ;

fragment HEX
    : [0-9a-fA-F]
    ;

fragment SAFE_CODEPOINT
    : ~ ["\\\u0000-\u001F]
    ;

NUMBER
    : '-'? INT ('.' [0-9] +)? EXP?
    ;

fragment INT
    : '0'
    | [1-9] [0-9]*
    ;

fragment EXP
    : [Ee] [+\-]? INT
    ;

TRUE
    : 'true'
    ;

FALSE
    : 'false'
    ;

NULL
    : 'null'
    ;

WS
    : [ \t\n\r] + -> skip
    ;
