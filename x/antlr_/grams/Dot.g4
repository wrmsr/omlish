/*
Copyright (c) 2013 Terence Parr
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

3. The name of the author may not be used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
/*
https://github.com/antlr/grammars-v4/blob/f9b1c203dc6368d972bedcb6f8c3670688ad8008/dot/DOT.g4

Derived from http://www.graphviz.org/doc/info/lang.html. Comments pulled from spec.
*/
grammar Dot;


graph
    : STRICT? (GRAPH | DIGRAPH) ident? '{' stmtList '}'
    ;

stmtList
    : (stmt ';'?)*
    ;

stmt
    : nodeStmt | edgeStmt | attrStmt | ident '=' ident | subgraph
    ;

attrStmt
    : (GRAPH | NODE | EDGE) attrList
    ;

attrList
    : ('[' aList? ']')+
    ;

aList
    : (ident ('=' ident)? ','?)+
    ;

edgeStmt
    : (nodeId | subgraph) edgeRHS attrList?
    ;

edgeRHS
    : (edgeop (nodeId | subgraph))+
    ;

edgeop
    : '->' | '--'
    ;

nodeStmt
    : nodeId attrList?
    ;

nodeId
    : ident port?
    ;

port
    : ':' ident (':' ident)?
    ;

subgraph
    : (SUBGRAPH ident?)? '{' stmtList '}'
    ;

ident
    : IDENT | STRING | HTML_STRING | NUMBER
    ;

// The keywords node, edge, graph, digraph, subgraph, and strict are case-independent
STRICT
    : [Ss] [Tt] [Rr] [Ii] [Cc] [Tt]
    ;

GRAPH
    : [Gg] [Rr] [Aa] [Pp] [Hh]
    ;

DIGRAPH
    : [Dd] [Ii] [Gg] [Rr] [Aa] [Pp] [Hh]
    ;

NODE
    : [Nn] [Oo] [Dd] [Ee]
    ;

EDGE
    : [Ee] [Dd] [Gg] [Ee]
    ;

SUBGRAPH
    : [Ss] [Uu] [Bb] [Gg] [Rr] [Aa] [Pp] [Hh]
    ;

// A numeral [-]?(.[0-9]+|[0-9]+(.[0-9]*)?)"
NUMBER
    : '-'? ('.' DIGIT+ | DIGIT+ ('.' DIGIT*)?)
    ;

fragment DIGIT
    : [0-9]
    ;

// Any double-quoted string ("...") possibly containing escaped quotes
STRING
    : '"' ('\\"' | .)*? '"'
    ;

// Any string of alphabetic ([a-zA-Z\200-\377]) characters, underscores  ('_') or digits ([0-9]), not beginning with a
// digit
IDENT
    : LETTER (LETTER | DIGIT)*
    ;

fragment LETTER
    : [a-zA-Z\u0080-\u00FF_]
    ;

// HTML strings, angle brackets must occur in matched pairs, and *  unescaped newlines are allowed.
HTML_STRING
    : '<' (TAG | ~ [<>])* '>'
    ;

fragment TAG
    : '<' .*? '>'
    ;

COMMENT
    : '/*' .*? '*/' -> skip
    ;

LINE_COMMENT
    : '//' .*? '\r'? '\n' -> skip
    ;

// A '#' character is considered a line output from a C preprocessor (e.g., # 34 to indicate line 34) and discarded
PREPROC
    : '#' ~[\r\n]* -> skip
    ;

WS
    : [ \t\n\r]+ -> skip
    ;
