grammar Minisql;


tokens {
    DELIMITER
}


singleStmt
    : select ';' EOF
    ;

select
    : cteSelect
    ;

cteSelect
    : (WITH cte (',' cte)*)? unionSelect
    ;

cte
    : ident AS '(' select ')'
    ;

unionSelect
    : primarySelect unionItem*
    ;

unionItem
    : UNION setQuantifier? primarySelect
    ;

primarySelect
    : SELECT setQuantifier? selectItem (',' selectItem)*
      (FROM relation (',' relation)*)?
      (WHERE where=booleanExpr)?
      (GROUP BY groupBy)?
      (HAVING having=booleanExpr)?
      (ORDER BY sortItem (',' sortItem)*)?
    ;

selectItem
    : '*'                      #allSelectItem
    | expr (AS? ident)?  #exprSelectItem
    ;

expr
    : booleanExpr
    ;

booleanExpr
    : valueExpr predicate[$valueExpr.ctx]?   #predicatedBooleanExpr
    | op=NOT booleanExpr                     #unaryBooleanExpr
    | booleanExpr op=(AND | OR) booleanExpr  #binaryBooleanExpr
    | booleanExpr '::' ident                 #castBooleanExpr
    ;

predicate[ParserRuleContext value]
    : cmpOp right=valueExpr             #cmpPredicate
    | IS NOT? NULL                      #isNullPredicate
    | NOT? IN '(' expr (',' expr)* ')'  #inListPredicate
    | NOT? IN '(' select ')'            #inSelectPredicate
    | NOT? LIKE expr                    #likePredicate
    ;

valueExpr
    : primaryExpr                                #primaryValueExpr
    | op=unaryOp valueExpr                       #unaryValueExpr
    | left=valueExpr op=arithOp right=valueExpr  #arithValueExpr
    ;

primaryExpr
    : qualifiedName '(' (expr (',' expr)*)? ')' over?  #functionCallExpr
    | qualifiedName '(' '*' ')' over?                  #starFunctionCallExpr
    | CASE caseItem* (ELSE expr)? END                  #caseExpr
    | '(' select ')'                                   #selectExpr
    | '(' expr ')'                                     #parenExpr
    | simpleExpr                                       #simplePrimaryExpr
    ;

simpleExpr
    : qualifiedName
    | number
    | string
    | null
    | true
    | false
    ;

caseItem
    : WHEN expr THEN expr
    ;

over
    : OVER '(' (ORDER BY sortItem (',' sortItem)*)? ')'
    ;

sortItem
    : expr direction=(ASC | DESC)?
    ;

relation
    : relation AS? ident      #aliasedRelation
    | left=relation
      ty=joinType?
      JOIN right=relation
      (ON cond=booleanExpr)?  #joinRelation
    | '(' select ')'          #selectRelation
    | '(' relation ')'        #parenRelation
    | qualifiedName           #tableRelation
    ;

groupBy
    : expr (',' expr)*
    ;

qualifiedName
    : ident ('.' ident)*
    ;

identList
    : ident (',' ident)*
    ;

ident
    : unquotedIdent
    | quotedIdent
    ;

quotedIdent
    : QUOTED_IDENT
    ;

number
    : INTEGER_VALUE  #integerNumber
    | DECIMAL_VALUE  #decimalNumber
    | FLOAT_VALUE    #floatNumber
    ;

string
    : STRING
    ;

null
    : NULL
    ;

true
    : TRUE
    ;

false
    : FALSE
    ;

setQuantifier
    : DISTINCT
    | ALL
    ;

joinType
    : INNER
    | LEFT
    | LEFT OUTER
    | RIGHT
    | RIGHT OUTER
    | FULL
    | FULL OUTER
    | CROSS
    | NATURAL
    ;

cmpOp
    : '='
    | '!='
    | '<>'
    | '<'
    | '<='
    | '>'
    | '>='
    ;

arithOp
    : '+'
    | '-'
    | '*'
    | '/'
    | '%'
    | '||'
    ;

unaryOp
    : '+'
    | '-'
    ;

unquotedIdent
    : IDENT

    | LEFT
    | RIGHT

    ;

ALL: 'all';
AND: 'and';
AS: 'as';
ASC: 'asc';
BY: 'by';
CASE: 'case';
CROSS: 'cross';
DESC: 'desc';
DISTINCT: 'distinct';
ELSE: 'else';
END: 'end';
FALSE: 'false';
FROM: 'from';
FULL: 'full';
GROUP: 'group';
HAVING: 'having';
IN: 'in';
INNER: 'inner';
IS: 'is';
JOIN: 'join';
LEFT: 'left';
LIKE: 'like';
NATURAL: 'natural';
NOT: 'not';
NULL: 'null';
ON: 'on';
OR: 'or';
ORDER: 'order';
OUTER: 'outer';
OVER: 'over';
RIGHT: 'right';
SELECT: 'select';
THEN: 'then';
TRUE: 'true';
UNION: 'union';
WHEN: 'when';
WHERE: 'where';
WITH: 'with';

STRING
    : '\'' (~'\'' | '\'\'')* '\''
    ;

INTEGER_VALUE
    : DIGIT+
    ;

DECIMAL_VALUE
    : DIGIT+ '.' DIGIT*
    | '.' DIGIT+
    ;

FLOAT_VALUE
    : DIGIT+ ('.' DIGIT*)? EXPONENT
    | '.' DIGIT+ EXPONENT
    ;

IDENT
    : (LETTER | '_') (LETTER | DIGIT | '_' | '@' | ':' | '$')*
    ;

QUOTED_IDENT
    : '"' (~'"' | '""')* '"'
    ;

fragment EXPONENT
    : [Ee] [+-]? DIGIT+
    ;

fragment DIGIT
    : [0-9]
    ;

fragment LETTER
    : [A-Za-z]
    ;

COMMENT
    : '--' ~[\r\n]* '\r'? '\n'? -> channel(HIDDEN)
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> channel(HIDDEN)
    ;

WS
    : [ \t\n\r]+ -> skip
    ;
