/*
  1  makefile: statements "end of file"
  2          | "end of file"

  3  statements: br
  4            | statement
  5            | statements br
  6            | statements statement

  7  conditional: if_eq_kw condition statements_opt "endif" comment_opt br
  8             | if_eq_kw condition statements_opt "else" statements_opt "endif" comment_opt br
  9             | if_eq_kw condition statements_opt "else" conditional
 10             | if_def_kw identifier statements_opt "endif" comment_opt br
 11             | if_def_kw identifier statements_opt "else" statements_opt "endif" comment_opt br
 12             | if_def_kw identifier statements_opt "else" conditional

 13  conditional_in_recipe: if_eq_kw condition recipes_opt "endif" comment_opt
 14                       | if_eq_kw condition recipes_opt "else" recipes_opt "endif" comment_opt
 15                       | if_eq_kw condition recipes_opt "else" conditional_in_recipe
 16                       | if_def_kw identifier recipes_opt "endif" comment_opt
 17                       | if_def_kw identifier recipes_opt "else" recipes_opt "endif" comment_opt
 18                       | if_def_kw identifier recipes_opt "else" conditional_in_recipe

 19  condition: '(' expressions_opt ',' expressions_opt ')'
 20           | SLIT SLIT

 21  define: "define" pattern definition "endef" br
 22        | specifiers "define" pattern definition "endef" br
 23        | "define" pattern ASSIGN_OP definition "endef" br
 24        | specifiers "define" pattern ASSIGN_OP definition "endef" br

 25  definition: comment_opt br
 26            | comment_opt br exprs_in_def br

 27  include: "include" expressions br

 28  statements_opt: comment_opt br
 29                | comment_opt br statements

 30  if_def_kw: "ifdef"
 31           | "ifndef"

 32  if_eq_kw: "ifeq"
 33          | "ifneq"

 34  statement: COMMENT
 35           | assignment br
 36           | function br
 37           | rule
 38           | conditional
 39           | define
 40           | include
 41           | export br

 42  export: "export"
 43        | "unexport"
 44        | assignment_prefix
 45        | assignment_prefix WS targets

 46  assignment: pattern ASSIGN_OP comment_opt
 47            | pattern ASSIGN_OP exprs_in_assign comment_opt
 48            | assignment_prefix ASSIGN_OP comment_opt
 49            | assignment_prefix ASSIGN_OP exprs_in_assign comment_opt

 50  assignment_prefix: specifiers pattern

 51  specifiers: "override"
 52            | "export"
 53            | "unexport"
 54            | "override" "export"
 55            | "export" "override"
 56            | "undefine"
 57            | "override" "undefine"
 58            | "undefine" "override"

 59  expressions_opt: %empty
 60                 | expressions

 61  expressions: expression
 62             | expressions WS expression

 63  exprs_nested: expr_nested
 64              | exprs_nested WS expr_nested

 65  exprs_in_assign: expr_in_assign
 66                 | exprs_in_assign WS expr_in_assign

 67  exprs_in_def: first_expr_in_def
 68              | br
 69              | br first_expr_in_def
 70              | exprs_in_def br
 71              | exprs_in_def WS expr_in_recipe
 72              | exprs_in_def br first_expr_in_def

 73  first_expr_in_def: char_in_def expr_in_recipe
 74                   | function expr_in_recipe
 75                   | char_in_def
 76                   | function

 77  exprs_in_recipe: expr_in_recipe
 78                 | exprs_in_recipe WS expr_in_recipe

 79  expression: expression_text
 80            | expression_function

 81  expr_nested: expr_text_nested
 82             | expr_func_nested

 83  expr_in_assign: expr_text_in_assign
 84                | expr_func_in_assign

 85  expr_in_recipe: expr_text_in_recipe
 86                | expr_func_in_recipe

 87  expression_text: text
 88                 | expression_function text

 89  expr_text_nested: text_nested
 90                  | expr_func_nested text_nested

 91  expr_text_in_assign: text_in_assign
 92                     | expr_func_in_assign text_in_assign

 93  expr_text_in_recipe: text_in_recipe
 94                     | expr_func_in_recipe text_in_recipe

 95  expression_function: function
 96                     | '(' exprs_nested ')'
 97                     | expression_text function
 98                     | expression_function function

 99  expr_func_nested: function
100                  | '(' exprs_nested ')'
101                  | expr_func_nested function
102                  | expr_text_nested function

103  expr_func_in_assign: function
104                     | expr_func_in_assign function
105                     | expr_text_in_assign function

106  expr_func_in_recipe: function
107                     | expr_func_in_recipe function
108                     | expr_text_in_recipe function

109  function: VAR
110          | "$(" function_name ")"
111          | "$(" function_name WS arguments ")"
112          | "$(" function_name ',' arguments ")"
113          | "$(" function_name ':' expressions ")"
114          | "$(" function_name ASSIGN_OP expressions ")"

115  function_name: function_name_text
116               | function_name_function

117  function_name_text: function_name_piece
118                    | function_name_function function_name_piece

119  function_name_piece: CHARS
120                     | function_name_piece CHARS

121  function_name_function: function
122                        | function_name_text function

123  arguments: %empty
124           | argument
125           | arguments ','
126           | arguments ',' argument

127  argument: expressions

128  rule: targets colon prerequisites NL
129      | targets colon prerequisites recipes NL
130      | targets colon assignment NL

131  target: pattern

132  pattern: pattern_text
133         | pattern_function

134  pattern_text: identifier
135              | pattern_function identifier

136  pattern_function: function
137                  | pattern_text function
138                  | pattern_function function

139  prerequisites: %empty
140               | targets

141  targets: target
142         | targets WS target

143  recipes: recipe
144         | recipes recipe

145  recipes_opt: comment_opt NL
146             | comment_opt recipes NL

147  recipe: LEADING_TAB exprs_in_recipe
148        | NL conditional_in_recipe
149        | NL COMMENT

150  identifier: CHARS
151            | ','
152            | '('
153            | ')'
154            | identifier CHARS
155            | identifier keywords
156            | identifier ','
157            | identifier '('
158            | identifier ')'

159  text: char
160      | text char

161  text_nested: char_nested
162             | text_nested char_nested

163  text_in_assign: char_in_assign
164                | text_in_assign char_in_assign

165  text_in_recipe: char_in_recipe
166                | text_in_recipe char_in_recipe

167  char: CHARS
168      | SLIT
169      | ASSIGN_OP
170      | ':'

171  char_nested: char
172             | ','

173  char_in_assign: char_nested
174                | '('
175                | ')'
176                | keywords

177  char_in_def: char
178             | '('
179             | ')'
180             | ','
181             | COMMENT
182             | "include"
183             | "override"
184             | "export"
185             | "unexport"
186             | "ifdef"
187             | "ifndef"
188             | "ifeq"
189             | "ifneq"
190             | "else"
191             | "endif"
192             | "define"
193             | "undefine"

194  char_in_recipe: char_in_assign
195                | COMMENT

196  keywords: "include"
197          | "override"
198          | "export"
199          | "unexport"
200          | "ifdef"
201          | "ifndef"
202          | "ifeq"
203          | "ifneq"
204          | "else"
205          | "endif"
206          | "define"
207          | "endef"
208          | "undefine"

209  br: NL
210    | LEADING_TAB

211  colon: ':'
212       | ':' ':'

213  comment_opt: %empty
214             | COMMENT
Some lexer details

All in ' and almost all in " quotes are literals.
')' ::= <unpaired )>
'}' ::= <unpaired }>
"$(" ::= "$(" | "${" – beginning of an expansion
")" ::= ")" | "}" – ending of an expansion
"end of file" ::= <end of file>
COMMENT ::= <# comment (can be multiline)>
ASSIGN_OP ::= "=" | "?=" | ":=" | "::=" | "+=" | "!="
CHARS ::= <sequence of non-whitespace>
WS ::= <sequence of whitespace>
NL ::= "\n" | "\r" | "\r\n"
VAR ::= /\$./
SLIT ::= <single- or double-quote literal>
LEADING_TAB ::= <tabulation at the first position in a line (eats NL)>
*/
grammar Make;


makefile
    : EOF
    ;
