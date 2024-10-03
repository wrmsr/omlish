/*
 [The "BSD licence"]
 Copyright (c) 2013 Sam Harwell
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
/** C 2011 grammar built from the C11 Spec */
grammar C;


primaryExpression
    : IDENTIFIER
    | CONSTANT
    | STRING_LITERAL+
    | '(' expression ')'
    | genericSelection
    | EXTENSION? '(' compoundStatement ')'  // Blocks (GCC extension)
    | BUILTIN_VA_ARG '(' unaryExpression ',' typeName ')'
    | BUILTIN_OFFSETOF '(' typeName ',' unaryExpression ')'
    ;

genericSelection
    : GENERIC '(' assignmentExpression ',' genericAssocList ')'
    ;

genericAssocList
    : genericAssociation
    | genericAssocList ',' genericAssociation
    ;

genericAssociation
    : typeName ':' assignmentExpression
    | DEFAULT ':' assignmentExpression
    ;

postfixExpression
    : primaryExpression
    | postfixExpression '[' expression ']'
    | postfixExpression '(' argumentExpressionList? ')'
    | postfixExpression '.' IDENTIFIER
    | postfixExpression '->' IDENTIFIER
    | postfixExpression '++'
    | postfixExpression '--'
    | '(' typeName ')' '{' initializerList '}'
    | '(' typeName ')' '{' initializerList ',' '}'
    | EXTENSION '(' typeName ')' '{' initializerList '}'
    | EXTENSION '(' typeName ')' '{' initializerList ',' '}'
    ;

argumentExpressionList
    : assignmentExpression
    | argumentExpressionList ',' assignmentExpression
    ;

unaryExpression
    : postfixExpression
    | '++' unaryExpression
    | '--' unaryExpression
    | unaryOperator castExpression
    | SIZEOF unaryExpression
    | SIZEOF '(' typeName ')'
    | ALIGNOF '(' typeName ')'
    | '&&' IDENTIFIER  // GCC extension address of label
    ;

unaryOperator
    : '&'
    | '*'
    | '+'
    | '-'
    | '~'
    | '!'
    ;

castExpression
    : '(' typeName ')' castExpression
    | EXTENSION '(' typeName ')' castExpression
    | unaryExpression
    | DIGIT_SEQUENCE
    ;

multiplicativeExpression
    : castExpression
    | multiplicativeExpression '*' castExpression
    | multiplicativeExpression '/' castExpression
    | multiplicativeExpression '%' castExpression
    ;

additiveExpression
    : multiplicativeExpression
    | additiveExpression '+' multiplicativeExpression
    | additiveExpression '-' multiplicativeExpression
    ;

shiftExpression
    : additiveExpression
    | shiftExpression '<<' additiveExpression
    | shiftExpression '>>' additiveExpression
    ;

relationalExpression
    : shiftExpression
    | relationalExpression '<' shiftExpression
    | relationalExpression '>' shiftExpression
    | relationalExpression '<=' shiftExpression
    | relationalExpression '>=' shiftExpression
    ;

equalityExpression
    : relationalExpression
    | equalityExpression '==' relationalExpression
    | equalityExpression '!=' relationalExpression
    ;

andExpression
    : equalityExpression
    | andExpression '&' equalityExpression
    ;

exclusiveOrExpression
    : andExpression
    | exclusiveOrExpression '^' andExpression
    ;

inclusiveOrExpression
    : exclusiveOrExpression
    | inclusiveOrExpression '|' exclusiveOrExpression
    ;

logicalAndExpression
    : inclusiveOrExpression
    | logicalAndExpression '&&' inclusiveOrExpression
    ;

logicalOrExpression
    : logicalAndExpression
    | logicalOrExpression '||' logicalAndExpression
    ;

conditionalExpression
    : logicalOrExpression ('?' expression ':' conditionalExpression)?
    ;

assignmentExpression
    : conditionalExpression
    | unaryExpression assignmentOperator assignmentExpression
    | DIGIT_SEQUENCE
    ;

assignmentOperator
    : '='
    | '*='
    | '/='
    | '%='
    | '+='
    | '-='
    | '<<='
    | '>>='
    | '&='
    | '^='
    | '|='
    ;

expression
    : assignmentExpression
    | expression ',' assignmentExpression
    ;

constantExpression
    : conditionalExpression
    ;

declaration
    : declarationSpecifiers initDeclaratorList ';'
    | declarationSpecifiers ';'
    | staticAssertDeclaration
    ;

declarationSpecifiers
    : declarationSpecifier+
    ;

declarationSpecifiers2
    : declarationSpecifier+
    ;

declarationSpecifier
    : storageClassSpecifier
    | typeSpecifier
    | typeQualifier
    | functionSpecifier
    | alignmentSpecifier
    ;

initDeclaratorList
    : initDeclarator
    | initDeclaratorList ',' initDeclarator
    ;

initDeclarator
    : declarator
    | declarator '=' initializer
    ;

storageClassSpecifier
    : TYPEDEF
    | EXTERN
    | STATIC
    | THREADLOCAL
    | AUTO
    | REGISTER
    ;

typeSpecifier
    : ( VOID
      | CHAR
      | SHORT
      | INT
      | LONG
      | FLOAT
      | DOUBLE
      | SIGNED
      | UNSIGNED
      | BOOL
      | COMPLEX
      | M128
      | M128D
      | M128I
      )
    | EXTENSION '(' (M128 | M128D | M128I) ')'
    | atomicTypeSpecifier
    | structOrUnionSpecifier
    | enumSpecifier
    | typedefName
    | TYPEOF '(' constantExpression ')'  // GCC extension
    | typeSpecifier pointer
    ;

structOrUnionSpecifier
    : structOrUnion IDENTIFIER? '{' structDeclarationList '}'
    | structOrUnion IDENTIFIER
    ;

structOrUnion
    : STRUCT
    | UNION
    ;

structDeclarationList
    : structDeclaration
    | structDeclarationList structDeclaration
    ;

structDeclaration
    : specifierQualifierList structDeclaratorList? ';'
    | staticAssertDeclaration
    ;

specifierQualifierList
    : typeSpecifier specifierQualifierList?
    | typeQualifier specifierQualifierList?
    ;

structDeclaratorList
    : structDeclarator
    | structDeclaratorList ',' structDeclarator
    ;

structDeclarator
    : declarator
    | declarator? ':' constantExpression
    ;

enumSpecifier
    : ENUM IDENTIFIER? '{' enumeratorList '}'
    | ENUM IDENTIFIER? '{' enumeratorList ',' '}'
    | ENUM IDENTIFIER
    ;

enumeratorList
    : enumerator
    | enumeratorList ',' enumerator
    ;

enumerator
    : enumerationConstant
    | enumerationConstant '=' constantExpression
    ;

enumerationConstant
    : IDENTIFIER
    ;

atomicTypeSpecifier
    : ATOMIC '(' typeName ')'
    ;

typeQualifier
    : CONST
    | RESTRICT
    | VOLATILE
    | ATOMIC
    ;

functionSpecifier
    : ( INLINE
      | NORETURN
      | DUNDER_INLINE  // GCC extension
      | STDCALL
      )
    | gccAttributeSpecifier
    | DECLSPEC '(' IDENTIFIER ')'
    ;

alignmentSpecifier
    : ALIGNAS '(' typeName ')'
    | ALIGNAS '(' constantExpression ')'
    ;

declarator
    : pointer? directDeclarator gccDeclaratorExtension*
    ;

directDeclarator
    : IDENTIFIER
    | '(' declarator ')'
    | directDeclarator '[' typeQualifierList? assignmentExpression? ']'
    | directDeclarator '[' STATIC typeQualifierList? assignmentExpression ']'
    | directDeclarator '[' typeQualifierList STATIC assignmentExpression ']'
    | directDeclarator '[' typeQualifierList? '*' ']'
    | directDeclarator '(' parameterTypeList ')'
    | directDeclarator '(' identifierList? ')'
    | IDENTIFIER ':' DIGIT_SEQUENCE
    | '(' typeSpecifier? pointer directDeclarator ')'  // function pointer like: (__cdecl *f)
    ;

gccDeclaratorExtension
    : '__asm' '(' STRING_LITERAL+ ')'
    | gccAttributeSpecifier
    ;

gccAttributeSpecifier
    : ATTRIBUTE '(' '(' gccAttributeList ')' ')'
    ;

gccAttributeList
    : gccAttribute (',' gccAttribute)*
    | // empty
    ;

gccAttribute
    : ~(',' | '(' | ')') ('(' argumentExpressionList? ')')?  // relaxed def for "identifier or reserved word"
    | // empty
    ;

nestedParenthesesBlock
    : (~('(' | ')') | '(' nestedParenthesesBlock ')')*
    ;

pointer
    : '*' typeQualifierList?
    | '*' typeQualifierList? pointer
    | '^' typeQualifierList?  // Blocks language extension
    | '^' typeQualifierList? pointer  // Blocks language extension
    ;

typeQualifierList
    : typeQualifier
    | typeQualifierList typeQualifier
    ;

parameterTypeList
    : parameterList
    | parameterList ',' '...'
    ;

parameterList
    : parameterDeclaration
    | parameterList ',' parameterDeclaration
    ;

parameterDeclaration
    : declarationSpecifiers declarator
    | declarationSpecifiers2 abstractDeclarator?
    ;

identifierList
    : IDENTIFIER
    | identifierList ',' IDENTIFIER
    ;

typeName
    : specifierQualifierList abstractDeclarator?
    ;

abstractDeclarator
    : pointer
    | pointer? directAbstractDeclarator gccDeclaratorExtension*
    ;

directAbstractDeclarator
    : '(' abstractDeclarator ')' gccDeclaratorExtension*
    | '[' typeQualifierList? assignmentExpression? ']'
    | '[' STATIC typeQualifierList? assignmentExpression ']'
    | '[' typeQualifierList STATIC assignmentExpression ']'
    | '[' '*' ']'
    | '(' parameterTypeList? ')' gccDeclaratorExtension*
    | directAbstractDeclarator '[' typeQualifierList? assignmentExpression? ']'
    | directAbstractDeclarator '[' STATIC typeQualifierList? assignmentExpression ']'
    | directAbstractDeclarator '[' typeQualifierList STATIC assignmentExpression ']'
    | directAbstractDeclarator '[' '*' ']'
    | directAbstractDeclarator '(' parameterTypeList? ')' gccDeclaratorExtension*
    ;

typedefName
    : IDENTIFIER
    ;

initializer
    : assignmentExpression
    | '{' initializerList '}'
    | '{' initializerList ',' '}'
    ;

initializerList
    : designation? initializer
    | initializerList ',' designation? initializer
    ;

designation
    : designatorList '='
    ;

designatorList
    : designator
    | designatorList designator
    ;

designator
    : '[' constantExpression ']'
    | '.' IDENTIFIER
    ;

staticAssertDeclaration
    : STATICASSERT '(' constantExpression ',' STRING_LITERAL+ ')' ';'
    ;

statement
    : labeledStatement
    | compoundStatement
    | expressionStatement
    | selectionStatement
    | iterationStatement
    | jumpStatement
    | ('__asm' | '__asm__') (VOLATILE | DUNDER_VOLATILE) '('
      (logicalOrExpression (',' logicalOrExpression)*)?
      (':' (logicalOrExpression (',' logicalOrExpression)*)?)*
      ')' ';'
    ;

labeledStatement
    : IDENTIFIER ':' statement
    | CASE constantExpression ':' statement
    | DEFAULT ':' statement
    ;

compoundStatement
    : '{' blockItemList? '}'
    ;

blockItemList
    : blockItem
    | blockItemList blockItem
    ;

blockItem
    : statement
    | declaration
    ;

expressionStatement
    : expression? ';'
    ;

selectionStatement
    : IF '(' expression ')' statement (ELSE statement)?
    | SWITCH '(' expression ')' statement
    ;

iterationStatement
    : WHILE '(' expression ')' statement
    | DO statement WHILE '(' expression ')' ';'
    | FOR '(' forCondition ')' statement
    ;

forCondition
    : forDeclaration ';' forExpression? ';' forExpression?
    | expression? ';' forExpression? ';' forExpression?
    ;

forDeclaration
    : declarationSpecifiers initDeclaratorList
    | declarationSpecifiers
    ;

forExpression
    : assignmentExpression
    | forExpression ',' assignmentExpression
    ;

jumpStatement
    : GOTO IDENTIFIER ';'
    | CONTINUE ';'
    | BREAK ';'
    | RETURN expression? ';'
    | GOTO unaryExpression ';'  // GCC extension
    ;

compilationUnit
    : translationUnit? EOF
    ;

translationUnit
    : externalDeclaration
    | translationUnit externalDeclaration
    ;

externalDeclaration
    : functionDefinition
    | declaration
    | ';'
    ;

functionDefinition
    : declarationSpecifiers? declarator declarationList? compoundStatement
    ;

declarationList
    : declaration
    | declarationList declaration
    ;

AUTO: 'auto';
BREAK: 'break';
CASE: 'case';
CHAR: 'char';
CONST: 'const';
CONTINUE: 'continue';
DEFAULT: 'default';
DO: 'do';
DOUBLE: 'double';
ELSE: 'else';
ENUM: 'enum';
EXTERN: 'extern';
FLOAT: 'float';
FOR: 'for';
GOTO: 'goto';
IF: 'if';
INLINE: 'inline';
INT: 'int';
LONG: 'long';
REGISTER: 'register';
RESTRICT: 'restrict';
RETURN: 'return';
SHORT: 'short';
SIGNED: 'signed';
SIZEOF: 'sizeof';
STATIC: 'static';
STRUCT: 'struct';
SWITCH: 'switch';
TYPEDEF: 'typedef';
UNION: 'union';
UNSIGNED: 'unsigned';
VOID: 'void';
VOLATILE: 'volatile';
WHILE: 'while';

ALIGNAS: '_Alignas';
ALIGNOF: '_Alignof';
ATOMIC: '_Atomic';
BOOL: '_Bool';
COMPLEX: '_Complex';
GENERIC: '_Generic';
IMAGINARY: '_Imaginary';
NORETURN: '_Noreturn';
STATICASSERT: '_Static_assert';
THREADLOCAL: '_Thread_local';

M128: '__m128';
M128D: '__m128d';
M128I: '__m128i';

LEFTPAREN: '(';
RIGHTPAREN: ')';
LEFTBRACKET: '[';
RIGHTBRACKET: ']';
LEFTBRACE: '{';
RIGHTBRACE: '}';

LESS: '<';
LESSEQUAL: '<=';
GREATER: '>';
GREATEREQUAL: '>=';
LEFTSHIFT: '<<';
RIGHTSHIFT: '>>';

PLUS: '+';
PLUSPLUS: '++';
MINUS: '-';
MINUSMINUS: '--';
STAR: '*';
DIV: '/';
MOD: '%';

AND: '&';
OR: '|';
ANDAND: '&&';
OROR: '||';
CARET: '^';
NOT: '!';
TILDE: '~';

QUESTION: '?';
COLON: ':';
SEMI: ';';
COMMA: ',';

ASSIGN: '=';
STARASSIGN: '*=';
DIVASSIGN: '/=';
MODASSIGN: '%=';
PLUSASSIGN: '+=';
MINUSASSIGN: '-=';
LEFTSHIFTASSIGN: '<<=';
RIGHTSHIFTASSIGN: '>>=';
ANDASSIGN: '&=';
XORASSIGN: '^=';
ORASSIGN: '|=';

EQUAL: '==';
NOTEQUAL: '!=';

ARROW: '->';
DOT: '.';
ELLIPSIS: '...';

EXTENSION: '__extension__';
BUILTIN_VA_ARG: '__builtin_va_arg';
BUILTIN_OFFSETOF: '__builtin_offsetof';
TYPEOF: '__typeof__';
DUNDER_INLINE: '__inline__';
STDCALL: '__stdcall';
DECLSPEC: '__declspec';
ATTRIBUTE: '__attribute__';
DUNDER_VOLATILE: '__volatile__';

IDENTIFIER
    : IDENTIFIER_NONDIGIT (IDENTIFIER_NONDIGIT | DIGIT)*
    ;

fragment IDENTIFIER_NONDIGIT
    : NONDIGIT
    | UNIVERSAL_CHARACTER_NAME
    ;

fragment NONDIGIT
    : [a-zA-Z_]
    ;

fragment DIGIT
    : [0-9]
    ;

fragment UNIVERSAL_CHARACTER_NAME
    : '\\u' HEX_QUAD
    | '\\U' HEX_QUAD HEX_QUAD
    ;

fragment HEX_QUAD
    : HEXADECIMAL_DIGIT HEXADECIMAL_DIGIT HEXADECIMAL_DIGIT HEXADECIMAL_DIGIT
    ;

CONSTANT
    : INTEGER_CONSTANT
    | FLOATING_CONSTANT
    | CHARACTER_CONSTANT
    ;

fragment INTEGER_CONSTANT
    : DECIMAL_CONSTANT INTEGER_SUFFIX?
    | OCTAL_CONSTANT INTEGER_SUFFIX?
    | HEXADECIMAL_CONSTANT INTEGER_SUFFIX?
    | BINARY_CONSTANT
    ;

fragment BINARY_CONSTANT
    : '0' [bB] [0-1]+
    ;

fragment DECIMAL_CONSTANT
    : NONZERO_DIGIT DIGIT*
    ;

fragment OCTAL_CONSTANT
    : '0' OCTAL_DIGIT*
    ;

fragment HEXADECIMAL_CONSTANT
    : HEXADECIMAL_PREFIX HEXADECIMAL_DIGIT+
    ;

fragment HEXADECIMAL_PREFIX
    : '0' [xX]
    ;

fragment NONZERO_DIGIT
    : [1-9]
    ;

fragment OCTAL_DIGIT
    : [0-7]
    ;

fragment HEXADECIMAL_DIGIT
    : [0-9a-fA-F]
    ;

fragment INTEGER_SUFFIX
    : UNSIGNED_SUFFIX LONG_SUFFIX?
    | UNSIGNED_SUFFIX LONG_LONG_SUFFIX
    | LONG_SUFFIX UNSIGNED_SUFFIX?
    | LONG_LONG_SUFFIX UNSIGNED_SUFFIX?
    ;

fragment UNSIGNED_SUFFIX
    : [uU]
    ;

fragment LONG_SUFFIX
    : [lL]
    ;

fragment LONG_LONG_SUFFIX
    : 'll' | 'LL'
    ;

fragment FLOATING_CONSTANT
    : DECIMAL_FLOATING_CONSTANT
    | HEXADECIMAL_FLOATING_CONSTANT
    ;

fragment DECIMAL_FLOATING_CONSTANT
    : FRACTIONAL_CONSTANT EXPONENT_PART? FLOATING_SUFFIX?
    | DIGIT_SEQUENCE EXPONENT_PART FLOATING_SUFFIX?
    ;

fragment HEXADECIMAL_FLOATING_CONSTANT
    : HEXADECIMAL_PREFIX HEXADECIMAL_FRACTIONAL_CONSTANT BINARY_EXPONENT_PART FLOATING_SUFFIX?
    | HEXADECIMAL_PREFIX HEXADECIMAL_DIGIT_SEQUENCE BINARY_EXPONENT_PART FLOATING_SUFFIX?
    ;

fragment FRACTIONAL_CONSTANT
    : DIGIT_SEQUENCE? '.' DIGIT_SEQUENCE
    | DIGIT_SEQUENCE '.'
    ;

fragment EXPONENT_PART
    : 'e' SIGN? DIGIT_SEQUENCE
    | 'E' SIGN? DIGIT_SEQUENCE
    ;

fragment SIGN
    : '+' | '-'
    ;

DIGIT_SEQUENCE
    : DIGIT+
    ;

fragment HEXADECIMAL_FRACTIONAL_CONSTANT
    : HEXADECIMAL_DIGIT_SEQUENCE? '.' HEXADECIMAL_DIGIT_SEQUENCE
    | HEXADECIMAL_DIGIT_SEQUENCE '.'
    ;

fragment BINARY_EXPONENT_PART
    : 'p' SIGN? DIGIT_SEQUENCE
    | 'P' SIGN? DIGIT_SEQUENCE
    ;

fragment HEXADECIMAL_DIGIT_SEQUENCE
    : HEXADECIMAL_DIGIT+
    ;

fragment FLOATING_SUFFIX
    : 'f' | 'l' | 'F' | 'L'
    ;

fragment CHARACTER_CONSTANT
    : '\'' C_CHAR_SEQUENCE '\''
    | 'L\'' C_CHAR_SEQUENCE '\''
    | 'u\'' C_CHAR_SEQUENCE '\''
    | 'U\'' C_CHAR_SEQUENCE '\''
    ;

fragment C_CHAR_SEQUENCE
    : C_CHAR+
    ;

fragment C_CHAR
    : ~['\\\r\n]
    | ESCAPE_SEQUENCE
    ;

fragment ESCAPE_SEQUENCE
    : SIMPLE_ESCAPE_SEQUENCE
    | OCTAL_ESCAPE_SEQUENCE
    | HEXADECIMAL_ESCAPE_SEQUENCE
    | UNIVERSAL_CHARACTER_NAME
    ;

fragment SIMPLE_ESCAPE_SEQUENCE
    : '\\' ['"?abfnrtv\\]
    ;

fragment OCTAL_ESCAPE_SEQUENCE
    : '\\' OCTAL_DIGIT
    | '\\' OCTAL_DIGIT OCTAL_DIGIT
    | '\\' OCTAL_DIGIT OCTAL_DIGIT OCTAL_DIGIT
    ;

fragment HEXADECIMAL_ESCAPE_SEQUENCE
    : '\\x' HEXADECIMAL_DIGIT+
    ;

STRING_LITERAL
    : ENCODING_PREFIX? '"' S_CHAR_SEQUENCE? '"'
    ;

fragment ENCODING_PREFIX
    : 'u8'
    | 'u'
    | 'U'
    | 'L'
    ;

fragment S_CHAR_SEQUENCE
    : S_CHAR+
    ;

fragment S_CHAR
    : ~["\\\r\n]
    | ESCAPE_SEQUENCE
    | '\\\n'    // Added line
    | '\\\r\n'  // Added line
    ;

COMPLEX_DEFINE
    : '#' WHITESPACE? 'define'  ~[#\r\n]* -> skip
    ;

INCLUDE_DIRECTIVE
    : '#' WHITESPACE? 'include' WHITESPACE? (('"' ~[\r\n]* '"') | ('<' ~[\r\n]* '>' )) WHITESPACE? NEW_LINE -> skip
    ;

// ignore the following asm blocks: asm { mfspr x, 286; }
ASM_BLOCK
    : 'asm' ~'{'* '{' ~'}'* '}' -> skip
    ;

// ignore the lines generated by c preprocessor: '#line 1 "/home/dm/files/dk1.h" 1'
LINE_AFTER_PREPROCESSING
    : '#line' WHITESPACE* ~[\r\n]* -> skip
    ;

LINE_DIRECTIVE
    : '#' WHITESPACE? DECIMAL_CONSTANT WHITESPACE? STRING_LITERAL ~[\r\n]* -> skip
    ;

PRAGMA_DIRECTIVE
    : '#' WHITESPACE? 'pragma' WHITESPACE ~[\r\n]* -> skip
    ;

WHITESPACE
    : [ \t]+ -> skip
    ;

NEW_LINE
    : ('\r' '\n'? | '\n') -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;
