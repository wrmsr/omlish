grammar IceSql;


@header {
import dataclasses


@dataclasses.dataclass(frozen=True)
class IceSqlParserConfig:
    interval_units: bool = False


DEFAULT_ICE_SQL_PARSER_CONFIG = IceSqlParserConfig()
}


@parser::members {
_config = None

@property
def config(self):
    return self._config or DEFAULT_ICE_SQL_PARSER_CONFIG

@config.setter
def config(self, config):
    if self._config is not None or not isinstance(config, IceSqlParserConfig):
        raise TypeError
    self._config = config
}


tokens {
    DELIMITER
}


singleStatement
    : statement EOF
    ;

statement
    : select
    | createTable
    | insert
    | delete
    ;

createTable
    : CREATE (OR REPLACE)? TABLE qualifiedName ('(' colSpec (',' colSpec)* ')')? (AS select)?
    ;

colSpec
    : identifier typeSpec?
    ;

insert
    : INSERT INTO qualifiedName select
    ;

delete
    : DELETE FROM qualifiedName (WHERE where=booleanExpression)?
    ;

select
    : cteSelect
    ;

cteSelect
    : (WITH cte (',' cte)*)? setSelect
    ;

cte
    : identifier AS '(' select ')'
    ;

setSelect
    : parenSelect setSelectItem*
    ;

setSelectItem
    : setSelectKind setQuantifier? parenSelect
    ;

setSelectKind
    : INTERSECT
    | MINUS
    | EXCEPT
    | UNION ALL?
    ;

parenSelect
    : '(' parenSelect ')'
    | primarySelect
    ;

primarySelect
    : SELECT topN? setQuantifier? selectItem (',' selectItem)*
      (FROM relation (',' relation)*)?
      (WHERE where=booleanExpression)?
      (GROUP BY grouping)?
      (HAVING having=booleanExpression)?
      (QUALIFY qualify=booleanExpression)?
      (ORDER BY sortItem (',' sortItem)*)?
      (LIMIT INTEGER_VALUE)?
    ;

topN
    : TOP number
    ;

selectItem
    : '*'                           #allSelectItem
    | identifier '.' '*'            #identifierAllSelectItem
    | expression (AS? identifier)?  #expressionSelectItem
    ;

expression
    : booleanExpression
    ;

booleanExpression
    : valueExpression predicate[$valueExpression.ctx]?   #predicatedBooleanExpression
    | op=NOT booleanExpression                           #unaryBooleanExpression
    | booleanExpression op=(AND | OR) booleanExpression  #binaryBooleanExpression
    ;

predicate[ParserRuleContext value]
    : cmpOp right=valueExpression                                   #cmpPredicate
    | IS NOT? NULL                                                  #isNullPredicate
    | NOT? BETWEEN lower=valueExpression AND upper=valueExpression  #betweenPredicate
    | NOT? IN '(' expression (',' expression)* ')'                  #inListPredicate
    | NOT? IN '(' select ')'                                        #inSelectPredicate
    | NOT? IN JINJA                                                 #inJinjaPredicate
    | NOT? kind=(LIKE | ILIKE | RLIKE) ANY?
      (expression | ('(' expression (',' expression)* ')'))
      (ESCAPE esc=string)?                                          #likePredicate
    ;

valueExpression
    : primaryExpression                                      #primaryValueExpression
    | op=unaryOp valueExpression                             #unaryValueExpression
    | left=valueExpression op=arithOp right=valueExpression  #arithValueExpression
    | valueExpression
      (':' traversalKey | ':'? '[' traversalKey ']')
      ('.' traversalKey | '[' traversalKey ']')*             #traversalValueExpression
    | valueExpression '::' typeSpec                          #castValueExpression
    ;

traversalKey
    : identifier
    | string
    | integer
    ;

primaryExpression
    : functionCall                                                      #functionCallExpression
    | CASE (val=expression)? caseItem* (ELSE default=expression)? END   #caseExpression
    | { not self.config.interval_units }? INTERVAL expression           #intervalExpression
    | { self.config.interval_units }? INTERVAL expression intervalUnit  #intervalExpression
    | INTERVAL expression intervalUnit                                  #intervalExpression
    | '(' select ')'                                                    #selectExpression
    | '(' expression ')'                                                #parenExpression
    | CAST '(' expression AS typeSpec ')'                               #castCallExpression
    | DATE string                                                       #dateExpression
    | EXTRACT '(' part=identifier FROM value=expression ')'             #extractExpression
    | JINJA                                                             #jinjaExpression
    | simpleExpression                                                  #simplePrimaryExpression
    ;

simpleExpression
    : var
    | param
    | qualifiedName
    | number
    | string
    | null
    | true
    | false
    ;

typeSpec
    : identifier ('(' (simpleExpression (',' simpleExpression)*)? ')')?
    ;

functionCall
    : qualifiedName '(' setQuantifier? (expression (',' expression)*)? ')'
      ((IGNORE | RESPECT) NULLS)?
      (WITHIN GROUP '(' ORDER BY sortItem (',' sortItem)* ')')?
      over?                                                                     #expressionFunctionCall
    | qualifiedName '(' kwarg (',' kwarg)* ')'
      ((IGNORE | RESPECT) NULLS)?
      (WITHIN GROUP '(' ORDER BY sortItem (',' sortItem)* ')')?
      over?                                                                     #kwargFunctionCall
    | qualifiedName '(' setQuantifier? expression (IGNORE | RESPECT) NULLS ')'
      (WITHIN GROUP '(' ORDER BY sortItem (',' sortItem)* ')')?
      over?                                                                     #nullsFunctionCall
    | qualifiedName '(' '*' ')'
      over?                                                                     #starFunctionCall
    ;

kwarg
    : identifier '=>' expression
    ;

caseItem
    : WHEN expression THEN expression
    ;

intervalUnit
    : SECOND
    | MINUTE
    | HOUR
    | DAY
    | MONTH
    | YEAR
    ;

over
    : OVER '('
      (PARTITION BY (expression (',' expression)*))?
      (ORDER BY sortItem (',' sortItem)*)?
      frame? ')'
    ;

frameBound
    : INTEGER_VALUE (PRECEDING | FOLLOWING)  #numFrameBound
    | UNBOUNDED (PRECEDING | FOLLOWING)      #unboundedFrameBound
    | CURRENT ROW                            #currentRowFrameBound
    ;

frame
    : (ROWS | RANGE) frameBound                         #singleFrame
    | (ROWS | RANGE) BETWEEN frameBound AND frameBound  #doubleFrame
    ;

sortItem
    : expression direction=(ASC | DESC)? (NULLS (FIRST | LAST))?
    ;

relation
    : left=relation ty=joinType?
      JOIN right=relation
      (ON cond=booleanExpression)?
      (USING '(' using=identifierList ')')?                             #joinRelation
    | relation PIVOT '('
      func=qualifiedName '(' pc=identifier ')'
      FOR vc=identifier IN '(' (expression (',' expression)*)? ')' ')'  #pivotRelation
    | relation UNPIVOT '('
      vc=identifier
      FOR nc=identifier IN '(' identifierList? ')' ')'                  #unpivotRelation
    | LATERAL relation                                                  #lateralRelation
    | functionCall                                                      #functionCallRelation
    | '(' select ')'                                                    #selectRelation
    | '(' relation ')'                                                  #parenRelation
    | JINJA                                                             #jinjaRelation
    | relation AS? identifier ('(' identifierList ')')?                 #aliasedRelation
    | qualifiedName                                                     #tableRelation
    ;

grouping
    : expression (',' expression)*                          #flatGrouping
    | GROUPING SETS '(' groupingSet (',' groupingSet)* ')'  #setsGrouping
    ;

groupingSet
    : '(' expression (',' expression)* ')'
    ;

qualifiedName
    : identifier ('.' identifier)*
    ;

identifierList
    : identifier (',' identifier)*
    ;

identifier
    : unquotedIdentifier
    | quotedIdentifier
    ;

quotedIdentifier
    : QUOTED_IDENTIFIER
    ;

var
    : '$' IDENTIFIER
    ;

param
    : ':' IDENTIFIER
    ;

number
    : integer        #integerNumber
    | DECIMAL_VALUE  #decimalNumber
    | FLOAT_VALUE    #floatNumber
    ;

integer
    : INTEGER_VALUE
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

unquotedIdentifier
    : IDENTIFIER

    | CASE
    | DATE
    | DAY
    | EXTRACT
    | FIRST
    | GROUPING
    | HOUR
    | ILIKE
    | LAST
    | LEFT
    | LIKE
    | MINUTE
    | MONTH
    | OUTER
    | RANGE
    | REPLACE
    | RIGHT
    | RLIKE
    | SECOND
    | YEAR

    ;

ALL: 'all';
AND: 'and';
ANY: 'any';
AS: 'as';
ASC: 'asc';
BETWEEN: 'between';
BY: 'by';
CASE: 'case';
CAST: 'cast';
CREATE: 'create';
CROSS: 'cross';
CURRENT: 'current';
DATE: 'date';
DAY: 'day';
DELETE: 'delete';
DESC: 'desc';
DISTINCT: 'distinct';
DROP: 'drop';
ELSE: 'else';
END: 'end';
ESCAPE: 'escape';
EXCEPT: 'except';
EXTRACT: 'extract';
FALSE: 'false';
FIRST: 'first';
FOLLOWING: 'following';
FOR: 'for';
FROM: 'from';
FULL: 'full';
FUNCTION: 'function';
GROUP: 'group';
GROUPING: 'grouping';
HAVING: 'having';
HOUR: 'hour';
IGNORE: 'ignore';
ILIKE: 'ilike';
IN: 'in';
INNER: 'inner';
INSERT: 'insert';
INTERSECT: 'intersect';
INTERVAL: 'interval';
INTO: 'into';
IS: 'is';
JOIN: 'join';
LAST: 'last';
LATERAL: 'lateral';
LEFT: 'left';
LIKE: 'like';
LIMIT: 'limit';
MINUS: 'minus';
MINUTE: 'minute';
MONTH: 'month';
NATURAL: 'natural';
NOT: 'not';
NULL: 'null';
NULLS: 'nulls';
ON: 'on';
OR: 'or';
ORDER: 'order';
OUTER: 'outer';
OVER: 'over';
PARTITION: 'partition';
PIVOT: 'pivot';
PRECEDING: 'preceding';
QUALIFY: 'qualify';
RANGE: 'range';
REPLACE: 'replace';
RESPECT: 'respect';
RIGHT: 'right';
RLIKE: 'rlike';
ROW: 'row';
ROWS: 'rows';
SECOND: 'second';
SELECT: 'select';
SETS: 'sets';
TABLE: 'table';
THEN: 'then';
TOP: 'top';
TRUE: 'true';
UNBOUNDED: 'unbounded';
UNION: 'union';
UNPIVOT: 'unpivot';
USING: 'using';
WHEN: 'when';
WHERE: 'where';
WITH: 'with';
WITHIN: 'within';
YEAR: 'year';

STRING
    : '\'' (~'\'' | '\'\'' | '\\\'')* '\''
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

IDENTIFIER
    : (LETTER | '_') (LETTER | DIGIT | '_' | '@' | '$')*
    ;

QUOTED_IDENTIFIER
    : '"' (~'"' | '""')* '"'
    ;

JINJA
    : '{{' .*? '}}'
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

JINJA_STATEMENT
    : '{%' .*? '%}' -> channel(HIDDEN)
    ;

JINJA_COMMENT
    : '{#' .*? '#}' -> channel(HIDDEN)
    ;

WS
    : [ \t\n\r]+ -> channel(HIDDEN)
    ;
