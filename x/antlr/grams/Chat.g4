grammar Chat;


chat
    : line+ EOF
    ;

line
    : (name command message)? NEWLINE
    ;

name
    : WORD WHITESPACE
    ;

command
    : (SAYS | SHOUTS) ':' WHITESPACE
    ;

message
    : (emoticon | link | color | mention | WORD | WHITESPACE)+
    ;

emoticon
    : ':' '-'? ')'
    | ':' '-'? '('
    ;

link
    : TEXT TEXT
    ;

color
    : '/' WORD '/' message '/'
    ;

mention
    : '@' WORD
    ;

fragment A
    : [Aa]
    ;

fragment S
    : [Ss]
    ;

fragment Y
    : [Yy]
    ;

fragment H
    : [Hh]
    ;

fragment O
    : [Oo]
    ;

fragment U
    : [Uu]
    ;

fragment T
    : [Tt]
    ;

fragment LOWERCASE
    : [a-z]
    ;

fragment UPPERCASE
    : [A-Z]
    ;

SAYS
    : S A Y S
    ;

SHOUTS
    : S H O U T S
    ;

WORD
    : (LOWERCASE | UPPERCASE | '_')+
    ;

WHITESPACE
    : (' ' | '\t')+
    ;

NEWLINE
    : ('\r'? '\n' | '\r')+
    ;

TEXT
    : ('[' | '(') ~[\])]+ (']' | ')')
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> channel(2)
    ;

COMMENT
    : '//' ~[\r\n]* -> channel(2)
    ;
