/*
https://github.com/antlr/grammars-v4/blob/f9b1c203dc6368d972bedcb6f8c3670688ad8008/protobuf3/Protobuf3.g4

A Protocol Buffers 3 grammar for ANTLR v4.

Derived and adapted from:
https://developers.google.com/protocol-buffers/docs/reference/proto3-spec

@author Marco Willemart
*/
grammar Protobuf3;


proto
    : syntax (syntaxExtra)* EOF
    ;

syntax
    : SYNTAX '=' (PROTO3_DOUBLE | PROTO3_SINGLE) ';'
    ;

syntaxExtra
    : importStmt
    | packageStmt
    | option
    | topLevelDef
    | emptyStmt
    ;

importStmt
    : IMPORT (WEAK | PUBLIC)? STR_LIT ';'
    ;

packageStmt
    : PACKAGE fullIdent ';'
    ;

option
    : OPTION optionName '=' (constant | optionBody)  ';'
    ;

optionName
    : (IDENT | '(' fullIdent ')') ('.' (IDENT | reservedWord))*
    ;

optionBody
    : '{' (optionBodyVariable)* '}'
    ;

optionBodyVariable
    : optionName ':' constant
    ;

topLevelDef
    : message
    | enumDef
    | extend
    | service
    ;

message
    : MESSAGE messageName messageBody
    ;

messageBody
    : '{' (messageBodyContent)* '}'
    ;

messageBodyContent
    : field
    | enumDef
    | message
    | extend
    | option
    | oneof
    | mapField
    | reserved
    | emptyStmt
    ;

enumDef
    : ENUM enumName enumBody
    ;

enumBody
    : '{' (option | enumField | emptyStmt)* '}'
    ;

enumField
    : IDENT '=' '-'? INT_LIT ('[' enumValueOption (','  enumValueOption)* ']')? ';'
    ;

enumValueOption
    : optionName '=' constant
    ;

extend
    : EXTEND messageType '{' (field | emptyStmt) '}'
    ;

service
    : SERVICE serviceName '{' (option | rpc | emptyStmt)* '}'
    ;

rpc
    : RPC rpcName '(' STREAM? messageType ')'
      RETURNS '(' STREAM? messageType ')'
      (('{' (option | emptyStmt)* '}') | ';')
    ;

reserved
    : RESERVED (ranges | fieldNames) ';'
    ;

ranges
    : rangeRule (',' rangeRule)*
    ;

rangeRule
    : INT_LIT
    | INT_LIT TO INT_LIT
    ;

fieldNames
    : STR_LIT (',' STR_LIT)*
    ;

typeRule
    : simpleType
    | messageOrEnumType
    ;

simpleType
    : DOUBLE
    | FLOAT
    | INT32
    | INT64
    | UINT32
    | UINT64
    | SINT32
    | SINT64
    | FIXED32
    | FIXED64
    | SFIXED32
    | SFIXED64
    | BOOL
    | STRING
    | BYTES
    ;

fieldNumber
    : INT_LIT
    ;

field
    : REPEATED? typeRule fieldName '=' fieldNumber ('[' fieldOptions ']')? ';'
    ;

fieldOptions
    : fieldOption (','  fieldOption)*
    ;

fieldOption
    : optionName '=' constant
    ;

oneof
    : ONEOF oneofName '{' (oneofField | emptyStmt)* '}'
    ;

oneofField
    : typeRule fieldName '=' fieldNumber ('[' fieldOptions ']')? ';'
    ;

mapField
    : MAP '<' keyType ',' typeRule '>' mapName '=' fieldNumber ('[' fieldOptions ']')? ';'
    ;

keyType
    : INT32
    | INT64
    | UINT32
    | UINT64
    | SINT32
    | SINT64
    | FIXED32
    | FIXED64
    | SFIXED32
    | SFIXED64
    | BOOL
    | STRING
    ;

reservedWord
    : EXTEND
    | MESSAGE
    | OPTION
    | PACKAGE
    | RPC
    | SERVICE
    | STREAM
    | STRING
    | SYNTAX
    | WEAK
    ;

fullIdent
    : IDENT ('.' IDENT)*
    ;

messageName
    : IDENT
    ;

enumName
    : IDENT
    ;

messageOrEnumName
    : IDENT
    ;

fieldName
    : IDENT
    | reservedWord
    ;

oneofName
    : IDENT
    ;

mapName
    : IDENT
    ;

serviceName
    : IDENT
    ;

rpcName
    : IDENT
    ;

messageType
    : '.'? (IDENT '.')* messageName
    ;

messageOrEnumType
    : '.'? ((IDENT | reservedWord) '.')* messageOrEnumName
    ;

emptyStmt
    : ';'
    ;

constant
    : fullIdent
    | ('-' | '+')? INT_LIT
    | ('-' | '+')? FLOAT_LIT
    | STR_LIT
    | BOOL_LIT
    ;

BOOL: 'bool';
BYTES: 'bytes';
DOUBLE: 'double';
ENUM: 'enum';
EXTEND: 'extend';
FIXED32: 'fixed32';
FIXED64: 'fixed64';
FLOAT: 'float';
IMPORT: 'import';
INT32: 'int32';
INT64: 'int64';
MAP: 'map';
MESSAGE: 'message';
ONEOF: 'oneof';
OPTION: 'option';
PACKAGE: 'package';
PROTO3_DOUBLE: '"proto3"';
PROTO3_SINGLE: '\'proto3\'';
PUBLIC: 'public';
REPEATED: 'repeated';
RESERVED: 'reserved';
RETURNS: 'returns';
RPC: 'rpc';
SERVICE: 'service';
SFIXED32: 'sfixed32';
SFIXED64: 'sfixed64';
SINT32: 'sint32';
SINT64: 'sint64';
STREAM: 'stream';
STRING: 'string';
SYNTAX: 'syntax';
TO: 'to';
UINT32: 'uint32';
UINT64: 'uint64';
WEAK: 'weak';

fragment LETTER
    : [A-Za-z_]
    ;

fragment DECIMAL_DIGIT
    : [0-9]
    ;

fragment OCTAL_DIGIT
    : [0-7]
    ;

fragment HEX_DIGIT
    : [0-9A-Fa-f]
    ;

IDENT
    : LETTER (LETTER | DECIMAL_DIGIT)*
    ;

INT_LIT
    : DECIMAL_LIT
    | OCTAL_LIT
    | HEX_LIT
    ;

fragment DECIMAL_LIT
    : [1-9] DECIMAL_DIGIT*
    ;

fragment OCTAL_LIT
    : '0' OCTAL_DIGIT*
    ;

fragment HEX_LIT
    : '0' ('x' | 'X') HEX_DIGIT+
    ;

FLOAT_LIT
    : (DECIMALS '.' DECIMALS? EXPONENT? | DECIMALS EXPONENT | '.' DECIMALS EXPONENT?)
    | 'inf'
    | 'nan'
    ;

fragment DECIMALS
    : DECIMAL_DIGIT+
    ;

fragment EXPONENT
    : ('e' | 'E') ('+' | '-')? DECIMALS
    ;

BOOL_LIT
    : 'true'
    | 'false'
    ;

STR_LIT
    : '\'' CHAR_VALUE* '\''
    | '"' CHAR_VALUE* '"'
    ;

fragment CHAR_VALUE
    : HEX_ESCAPE
    | OCT_ESCAPE
    | CHAR_ESCAPE
    | ~[\u0000\n\\]
    ;

fragment HEX_ESCAPE
    : '\\' ('x' | 'X') HEX_DIGIT HEX_DIGIT
    ;

fragment OCT_ESCAPE
    : '\\' OCTAL_DIGIT OCTAL_DIGIT OCTAL_DIGIT
    ;

fragment CHAR_ESCAPE
    : '\\' [abfnrtv\\'"]
    ;

QUOTE
    : '\''
    | '"'
    ;

WS
    : [ \t\r\n\u000C]+ -> channel(2)
    ;

COMMENT
    : '/*' .*? '*/' -> channel(2)
    ;

LINE_COMMENT
    : '//' ~[\r\n]* -> channel(2)
    ;
