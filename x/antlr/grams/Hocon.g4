/*
https://github.com/jdevelop/go-hocon/blob/3818818d1e40850f3d5f4337a08d40988ce577e5/parser/HOCON.g4
*/
grammar Hocon;


hocon
    : obj*
    | array*
    | prop*
    ;

prop
    : objectData
    | arrayData
    | stringData
    | referenceData
    | numberData
    ;

obj
    : objectBegin prop (','? prop)* objectEnd
    | objectBegin objectEnd
    ;

objectBegin
    : '{'
    ;

objectEnd
    : '}'
    ;

objectData
    : key KV? obj
    ;

arrayData
    : key KV array
    ;

stringData
    : key KV stringValue
    ;

referenceData
    : key KV REFERENCE
    ;

numberData
    : key KV NUMBER
    ;

key
    : path
    | STRING
    ;

path
    : PATH_ELEMENT ('.' PATH_ELEMENT)*
    ;

arrayBegin
    : '['
    ;

arrayEnd
    : ']'
    ;

array
    : arrayBegin arrayValue (','? arrayValue)* arrayEnd
    | arrayBegin arrayEnd
    ;

arrayValue
    : arrayString
    | arrayReference
    | arrayNumber
    | arrayObj
    | arrayArray
    ;

arrayString
    : stringValue
    ;

arrayReference
    : REFERENCE
    ;

arrayNumber
    : NUMBER
    ;

arrayObj
    : obj
    ;

arrayArray
    : array
    ;

stringValue
    : STRING stringValue*         #v_string
    | rawstring stringValue*     #v_rawstring
    | REFERENCE stringValue*     #v_reference
    ;

rawstring
    : (PATH_ELEMENT|'-')+
    ;

fragment ESC
    : '\\' (["\\/bfnrt] | UNICODE)
    ;

fragment UNICODE
    : 'u' HEX HEX HEX HEX
    ;

fragment ALPHANUM
    : ('0' .. '9') | ('a'..'z') | ('A' .. 'Z')
    ;

fragment HEX
    : [0-9a-fA-F]
    ;

fragment INT
    : '0' | [1-9] [0-9]*
    ;

fragment EXP
    : [Ee] [+\-]? INT
    ;

COMMENT
    : ('#'|'//') ~('\r' | '\n')* -> skip
    ;

NUMBER
    : '-'? INT '.' [0-9] + EXP? | '-'? INT EXP | '-'? INT
    ;

STRING
    : '"' (ESC | ~ ["\\])* '"'
    | '\'' (ESC | ~ ['\\])* '\''
    ;

PATH_ELEMENT
    : (ALPHANUM|'-'|'_')+
    ;

REFERENCE
    : '${' PATH_ELEMENT ('.' PATH_ELEMENT)* '}'
    ;

KV
    : [=:]
    ;

WS
    : [ \t\n\r] + -> skip
    ;
