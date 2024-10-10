/*
Copyright (c) 2016, Burt AB
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
/*
https://github.com/burtcorp/jmespath-java/blob/f119644209001be06bdc6382d6f5cc9c5098a9fe/jmespath-core/src/main/antlr4/io/burt/jmespath/parser/JmesPath.g4
*/
grammar Jmespath;


singleExpression
    : expression EOF
    ;

expression
    : expression '.' chainedExpression  #chainExpression
    | expression bracketSpecifier       #bracketedExpression
    | bracketSpecifier                  #bracketExpression
    | expression COMPARATOR expression  #comparisonExpression
    | expression '&&' expression        #andExpression
    | expression '||' expression        #orExpression
    | identifier                        #identifierExpression
    | '!' expression                    #notExpression
    | '(' expression ')'                #parenExpression
    | wildcard                          #wildcardExpression
    | multiSelectList                   #multiSelectListExpression
    | multiSelectHash                   #multiSelectHashExpression
    | literal                           #literalExpression
    | functionExpression                #functionCallExpression
    | expression '|' expression         #pipeExpression
    | RAW_STRING                        #rawStringExpression
    | currentNode                       #currentNodeExpression
    | parameterNode                     #parameterExpression
    ;

chainedExpression
    : identifier
    | multiSelectList
    | multiSelectHash
    | functionExpression
    | wildcard
    ;

wildcard
    : '*'
    ;

bracketSpecifier
    : '[' SIGNED_INT ']'   #bracketIndex
    | '[' '*' ']'          #bracketStar
    | '[' sliceNode ']'    #bracketSlice
    | '[' ']'              #bracketFlatten
    | '[?' expression ']'  #select
    ;

multiSelectList
    : '[' expression (',' expression)* ']'
    ;

multiSelectHash
    : '{' keyvalExpr (',' keyvalExpr)* '}'
    ;

keyvalExpr
    : identifier ':' expression
    ;

sliceNode
    : sliceStart=SIGNED_INT? ':' sliceStop=SIGNED_INT? (':' sliceStep=SIGNED_INT?)?
    ;

parameterNode
    : '$' NAME  #nameParameter
    | '$' INT   #numberParameter
    ;

functionExpression
  : NAME '(' functionArg (',' functionArg)* ')'
  | NAME '(' ')'
  ;

functionArg
  : expression
  | expressionType
  ;

currentNode
    : '@'
    ;

expressionType
    : '&' expression
    ;

literal
    : '`' jsonValue '`'
    ;

identifier
    : NAME
    | STRING
    | JSON_CONSTANT
    ;

jsonObject
    : '{' jsonObjectPair (',' jsonObjectPair)* '}'
    | '{' '}'
    ;

jsonObjectPair
    : STRING ':' jsonValue
    ;

jsonArray
    : '[' jsonValue (',' jsonValue)* ']'
    | '[' ']'
    ;

jsonValue
    : STRING                                  #jsonStringValue
    | (REAL_OR_EXPONENT_NUMBER | SIGNED_INT)  #jsonNumberValue
    | jsonObject                              #jsonObjectValue
    | jsonArray                               #jsonArrayValue
    | JSON_CONSTANT                           #jsonConstantValue
    ;

COMPARATOR
    : '<'
    | '<='
    | '=='
    | '>='
    | '>'
    | '!='
    ;

RAW_STRING:
    '\'' (RAW_ESC | ~['\\])* '\''
    ;

fragment RAW_ESC
    : '\\' .
    ;

JSON_CONSTANT
    : 'true'
    | 'false'
    | 'null'
    ;

NAME
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

STRING
    : '"' (ESC | ~ ["\\])* '"'
    ;

fragment ESC
    : '\\' (["\\/bfnrt`] | UNICODE)
    ;

fragment UNICODE
    : 'u' HEX HEX HEX HEX
    ;

fragment HEX
    : [0-9a-fA-F]
    ;

REAL_OR_EXPONENT_NUMBER
    : '-'? INT '.' [0-9] + EXP?
    | '-'? INT EXP
    ;

SIGNED_INT
    : '-'? INT
    ;

INT
    : '0'
    | [1-9] [0-9]*
    ;

fragment EXP
    : [Ee] [+\-]? INT
    ;

WS
    : [ \t\n\r] + -> skip
    ;
