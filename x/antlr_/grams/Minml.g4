grammar Minml;


root
    : value
    ;

value
    : obj
    | array
    | string
    | number
    | true
    | false
    | null
    | identifier
    ;

obj
    : '{' pair (',' pair)* ','? '}'
    | '{' '}'
    ;

pair
    : k=value (':' v=value)?
    ;

array
    : '[' value (',' value)*  ','? ']'
    | '[' ']'
    ;

identifier
    : IDENTIFIER
    ;

string
    : TRI_DQ_STRING
    | TRI_SQ_STRING
    | DQ_STRING
    | SQ_STRING
    ;

number
    : NUMBER
    ;

true
    : TRUE
    ;

false
    : FALSE
    ;

null
    : NULL
    ;

FALSE: 'false';
NULL: 'null';
TRUE: 'true';

DQ_STRING
    : '"' (ESC | CP)* '"'
    ;

SQ_STRING
    : '\'' (ESC | CP)* '\''
    ;

TRI_DQ_STRING
    : '"""' (~'"' | '\\"' | ('"' ~'"') | ('""' ~'"'))* '"""'
    ;

TRI_SQ_STRING
    : '\'\'\'' (~'\'' | '\\\'' | ('\'' ~'\'') | ('\'\'' ~'\''))* '\'\'\''
    ;

IDENTIFIER
    : [A-Za-z_$] [A-Za-z_$0-9\-.]*
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

fragment CP
    : ~["\\\u0000-\u001F]
    ;

NUMBER
    : [+\-]? INT ('.' [0-9]*)? EXP?
    | [+\-]? '.' [0-9]* EXP?
    | [+\-]? '0x' HEX+
    ;

fragment EXP
    : [Ee] [+\-]? INT
    ;

fragment INT
    : [0-9]+
    ;

LINE_COMMENT
    : ('#' | '//') ~[\r\n]* '\r'? '\n'? -> channel(HIDDEN)
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

WS
    : [ \t\n\r] + -> skip
    ;
