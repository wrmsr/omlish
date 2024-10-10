/*
https://thrift.apache.org/docs/idl
*/
grammar Thrift;


document
    : header* definition* EOF
    ;

header
    : include
    | cppInclude
    | namespace
    ;

include
    : INCLUDE literal
    ;

cppInclude
    : CPP_INCLUDE literal
    ;

namespace
    : NAMESPACE namespaceScope identifier
    ;

namespaceScope
    : '*'
    | C_GLIB
    | CPP
    | CSHARP
    | DELPHI
    | GO
    | JAVA
    | JS
    | LUA
    | NETCORE
    | PERL
    | PHP
    | PY
    | PY_TWISTED
    | RB
    | ST
    | XSD
    ;

definition
    : const
    | typedef
    | enum
    | senum
    | struct
    | union
    | exception
    | service
    ;

const
    : CONST fieldType identifier '=' constValue listSeparator?
    ;

typedef
    : TYPEDEF definitionType identifier
    ;

enum
    : ENUM identifier '{' (identifier ('=' intConstant)? listSeparator?)* '}'
    ;

senum
    : SENUM identifier '{' (literal listSeparator?)* '}'
    ;

struct
    : STRUCT identifier XSD_ALL? '{' field* '}'
    ;

union
    : UNION identifier XSD_ALL? '{' field* '}'
    ;

exception
    : EXCEPTION identifier '{' field* '}'
    ;

service
    : SERVICE identifier (EXTENDS identifier)? '{' function* '}'
    ;

field
    : fieldID? fieldReq? fieldType identifier ('=' constValue)? xsdFieldOptions listSeparator?
    ;

fieldID
    : intConstant ':'
    ;

fieldReq
    : REQUIRED
    | OPTIONAL
    ;

xsdFieldOptions
    : XSD_OPTIONAL? XSD_NILLABLE? xsdAttrs?
    ;

xsdAttrs
    : XSD_ATTRS '{' field* '}'
    ;

function
    : ONEWAY? functionType identifier '(' field* ')' throws_? listSeparator?
    ;

functionType
    : fieldType | VOID
    ;

throws_
    : THROWS '(' field* ')'
    ;

fieldType
    : identifier
    | baseType
    | containerType
    ;

definitionType
    : baseType
    | containerType
    ;

baseType
    : BOOL
    | BYTE
    | I8
    | I16
    | I32
    | I64
    | DOUBLE
    | STRING
    | BINARY
    | SLIST
    ;

containerType
    : mapType
    | setType
    | listType
    ;

mapType
    : MAP cppType? '<' fieldType ',' fieldType '>'
    ;

setType
    : SET cppType? '<' fieldType '>'
    ;

listType
    : LIST '<' fieldType '>' cppType?
    ;

cppType
    : CPP_TYPE literal
    ;

constValue
    : intConstant
    | doubleConstant
    | literal
    | identifier
    | constList
    | constMap
    ;

intConstant
    : ('+' | '-')? DIGIT+
    ;

doubleConstant
    : ('+' | '-')? DIGIT+ ('.' DIGIT+)? (('E' | 'e') intConstant)?
    ;

constList
    : '[' (constValue listSeparator?)* ']'
    ;

constMap
    : '{' (constValue ':' constValue listSeparator?)* '}'
    ;

literal
    : (('"' ~'"'* '"') | ('\'' ~'\''* '\''))
    ;

listSeparator
    : ','
    | ';'
    ;

identifier
    : IDENTIFIER
    ;

BINARY: 'binary';
BOOL: 'bool';
BYTE: 'byte';
C_GLIB: 'c_glib';
CONST: 'const';
CPP: 'cpp';
CPP_INCLUDE: 'cpp_include';
CPP_TYPE: 'cpp_type';
CSHARP: 'csharp';
DELPHI: 'delphi';
DOUBLE: 'double';
ENUM: 'enum';
EXCEPTION: 'exception';
EXTENDS: 'extends';
GO: 'go';
I16: 'i16';
I32: 'i32';
I64: 'i64';
I8: 'i8';
INCLUDE: 'include';
JAVA: 'java';
JS: 'js';
LIST: 'list';
LUA: 'lua';
MAP: 'map';
NAMESPACE: 'namespace';
NETCORE: 'netcore';
ONEWAY: 'oneway';
OPTIONAL: 'optional';
PERL: 'perl';
PHP: 'php';
PY: 'py';
PY_TWISTED: 'py.twisted';
RB: 'rb';
REQUIRED: 'required';
SENUM: 'senum';
SERVICE: 'service';
SET: 'set';
SLIST: 'slist';
ST: 'st';
STRING: 'string';
STRUCT: 'struct';
THROWS: 'throws';
TYPEDEF: 'typedef';
UNION: 'union';
VOID: 'void';
XSD: 'xsd';
XSD_ALL: 'xsd_all';
XSD_ATTRS: 'xsd_attrs';
XSD_NILLABLE: 'xsd_nillable';
XSD_OPTIONAL: 'xsd_optional';

IDENTIFIER
    : (LETTER | '_') (LETTER | DIGIT | '.' | '_')*
    ;

fragment LETTER
    : 'A'..'Z'
    | 'a'..'z'
    ;

DIGIT
    : '0'..'9'
    ;

WS
    : [ \t\r\n\u000C]+ -> channel(2)
    ;

COMMENT
    : '/*' .*? '*/' -> channel(2)
    ;

LINE_COMMENT
    : ('//' | '#') ~[\r\n]* -> channel(2)
    ;
