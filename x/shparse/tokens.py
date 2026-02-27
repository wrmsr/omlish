# Copyright (c) 2016, Daniel Martí. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#   products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
r"""
type token uint32

# The list of all possible tokens.
const (
    ILLEGAL_TOK token = iota

    _EOF
    _NEWL
    _LIT
    _LIT_WORD
    _LIT_REDIR

    # Token values beyond this point stringify as exact source.
    _REAL_TOKEN_BOUNDARY

    SGL_QUOTE  # '
    DBL_QUOTE  # "
    BCK_QUOTE  # `

    AND      # &
    AND_AND  # &&
    OR_OR    # ||
    or       # |
    OR_AND   # |&

    DOLLAR          # $
    DOLL_SGL_QUOTE  # $'
    DOLL_DBL_QUOTE  # $"
    DOLL_BRACE      # ${
    DOLL_BRACK      # $[
    DOLL_PAREN      # $(
    DOLL_DBL_PAREN  # $((
    LEFT_BRACE      # {
    LEFT_BRACK      # [
    DBL_LEFT_BRACK  # [[
    LEFT_PAREN      # (
    DBL_LEFT_PAREN  # ((

    RIGHT_BRACE      # }
    RIGHT_BRACK      # ]
    DBL_RIGHT_BRACK  # ]]
    RIGHT_PAREN      # )
    DBL_RIGHT_PAREN  # ))
    SEMICOLON        # ;

    DBL_SEMICOLON  # ;;
    SEMI_AND       # ;&
    DBL_SEMI_AND   # ;;&
    SEMI_OR        # ;|

    EXCL_MARK  # !
    TILDE      # ~
    ADD_ADD    # ++
    SUB_SUB    # --
    STAR       # *
    POWER      # **
    EQUAL      # ==
    NEQUAL     # !=
    LEQUAL     # <=
    GEQUAL     # >=

    ADD_ASSGN       # +=
    SUB_ASSGN       # -=
    MUL_ASSGN       # *=
    QUO_ASSGN       # /=
    REM_ASSGN       # %=
    AND_ASSGN       # &=
    OR_ASSGN        # |=
    XOR_ASSGN       # ^=
    SHL_ASSGN       # <<=
    SHR_ASSGN       # >>=
    AND_BOOL_ASSGN  # &&=
    OR_BOOL_ASSGN   # ||=
    XOR_BOOL_ASSGN  # ^^=
    POW_ASSGN       # **=

    RDR_OUT        # >
    APP_OUT        # >>
    RDR_IN         # <
    RDR_IN_OUT     # <>
    DPL_IN         # <&
    DPL_OUT        # >&
    RDR_CLOB       # >|
    RDR_TRUNC      # >!
    APP_CLOB       # >>|
    APP_TRUNC      # >>!
    HDOC           # <<
    DASH_HDOC      # <<-
    WORD_HDOC      # <<<
    RDR_ALL        # &>
    RDR_ALL_CLOB   # &>|
    RDR_ALL_TRUNC  # &>!
    APP_ALL        # &>>
    APP_ALL_CLOB   # &>>|
    APP_ALL_TRUNC  # &>>!

    CMD_IN       # <(
    ASSGN_PAREN  # =(
    CMD_OUT      # >(

    PLUS       # +
    COL_PLUS   # :+
    MINUS      # -
    COL_MINUS  # :-
    QUEST      # ?
    COL_QUEST  # :?
    ASSGN      # =
    COL_ASSGN  # :=
    PERC       # %
    DBL_PERC   # %%
    HASH       # #
    DBL_HASH   # ##
    COL_HASH   # :#
    CARET      # ^
    DBL_CARET  # ^^
    COMMA      # ,
    DBL_COMMA  # ,,
    AT         # @
    SLASH      # /
    DBL_SLASH  # #
    PERIOD     # .
    COLON      # :

    TS_EXISTS    # -e
    TS_REG_FILE  # -f
    TS_DIRECT    # -d
    TS_CHAR_SP   # -c
    TS_BLCK_SP   # -b
    TS_NM_PIPE   # -p
    TS_SOCKET    # -S
    TS_SMB_LINK  # -L
    TS_STICKY    # -k
    TS_GID_SET   # -g
    TS_UID_SET   # -u
    TS_GRP_OWN   # -G
    TS_USR_OWN   # -O
    TS_MODIF     # -N
    TS_READ      # -r
    TS_WRITE     # -w
    TS_EXEC      # -x
    TS_NO_EMPTY  # -s
    TS_FD_TERM   # -t
    TS_EMP_STR   # -z
    TS_NEMP_STR  # -n
    TS_OPT_SET   # -o
    TS_VAR_SET   # -v
    TS_REF_VAR   # -R

    TS_RE_MATCH  # =~
    TS_NEWER     # -nt
    TS_OLDER     # -ot
    TS_DEV_INO   # -ef
    TS_EQL       # -eq
    TS_NEQ       # -ne
    TS_LEQ       # -le
    TS_GEQ       # -ge
    TS_LSS       # -lt
    TS_GTR       # -gt

    GLOB_QUEST  # ?(
    GLOB_STAR   # *(
    GLOB_PLUS   # +(
    GLOB_AT     # @(
    GLOB_EXCL   # !(
)


type RedirOperator token

const (
    RDR_OUT = RedirOperator(rdrOut) + iota  # >
    APP_OUT                                 # >>
    RDR_IN                                  # <
    RDR_IN_OUT                              # <>
    DPL_IN                                  # <&
    DPL_OUT                                 # >&
    RDR_CLOB                                # >|
    RDR_TRUNC                               # >! with [LangZsh]
    APP_CLOB                                # >>| with [LangZsh]
    APP_TRUNC                               # >>! with [LangZsh]
    HDOC                                    # <<
    DASH_HDOC                               # <<-
    WORD_HDOC                               # <<<
    RDR_ALL                                 # &>
    RDR_ALL_CLOB                            # &>| with [LangZsh]
    RDR_ALL_TRUNC                           # &>! with [LangZsh]
    APP_ALL                                 # &>>
    APP_ALL_CLOB                            # &>>| with [LangZsh]
    APP_ALL_TRUNC                           # &>>! with [LangZsh]

    # Deprecated: use [RdrClob]
    CLB_OUT = RDR_CLOB
)


type ProcOperator token

const (
    CMD_IN = ProcOperator(cmdIn) + iota  # <(
    CMD_IN_TEMP                          # =(
    CMD_OUT                              # >(
)


type GlobOperator token

const (
    GLOB_ZERO_OR_ONE = GlobOperator(globQuest) + iota  # ?(
    GLOB_ZERO_OR_MORE                                  # *(
    GLOB_ONE_OR_MORE                                   # +(
    GLOB_ONE                                           # @(
    GLOB_EXCEPT                                        # !(
)


type BinCmdOperator token

const (
    AND_STMT = BinCmdOperator(AND_AND) + iota  # &&
    OR_STMT                                    # ||
    PIPE                                       # |
    PIPE_ALL                                   # |&
)


type CaseOperator token

const (
    BREAK = CaseOperator(dblSemicolon) + iota  # ;;
    FALLTHROUGH                                # ;&
    RESUME                                     # ;;&
    RESUME_KORN                                # ;|
)


type ParNamesOperator token

const (
    NAMES_PREFIX       = ParNamesOperator(star)  # *
    NAMES_PREFIX_WORDS = ParNamesOperator(at)    # @
)


type ParExpOperator token

const (
    ALTERNATE_UNSET = ParExpOperator(plus) + iota  # +
    ALTERNATE_UNSET_OR_NULL                        # :+
    DEFAULT_UNSET                                  # -
    DEFAULT_UNSET_OR_NULL                          # :-
    ERROR_UNSET                                    # ?
    ERROR_UNSET_OR_NULL                            # :?
    ASSIGN_UNSET                                   # =
    ASSIGN_UNSET_OR_NULL                           # :=
    REM_SMALL_SUFFIX                               # %
    REM_LARGE_SUFFIX                               # %%
    REM_SMALL_PREFIX                               # #
    REM_LARGE_PREFIX                               # ##
    MATCH_EMPTY                                    # :# with [LangZsh]
    UPPER_FIRST                                    # ^
    UPPER_ALL                                      # ^^
    LOWER_FIRST                                    # ,
    LOWER_ALL                                      # ,,
    OTHER_PARAMOPS                                 # @
)


type UnAritOperator token

const (
    NOT          = UnAritOperator(exclMark) + iota  # !
    BIT_NEGATION                                    # ~
    INC                                             # ++
    DEC                                             # --
    PLUS         = UnAritOperator(plus)             # +
    MINUS        = UnAritOperator(minus)            # -
)


type BinAritOperator token

const (
    ADD = BinAritOperator(plus)    # +
    SUB = BinAritOperator(minus)   # -
    MUL = BinAritOperator(star)    # *
    QUO = BinAritOperator(slash)   # /
    REM = BinAritOperator(perc)    # %
    POW = BinAritOperator(power)   # **
    EQL = BinAritOperator(equal)   # ==
    GTR = BinAritOperator(rdrOut)  # >
    LSS = BinAritOperator(rdrIn)   # <
    NEQ = BinAritOperator(nequal)  # !=
    LEQ = BinAritOperator(lequal)  # <=
    GEQ = BinAritOperator(gequal)  # >=
    AND = BinAritOperator(and)     # &
    OR  = BinAritOperator(or)      # |
    XOR = BinAritOperator(caret)   # ^
    SHR = BinAritOperator(appOut)  # >>
    SHL = BinAritOperator(hdoc)    # <<

    # TODO: use "Bool" consistently for logical operators like AndArit and OrArit; use #go:fix inline?

    AND_ARIT   = BinAritOperator(AND_AND)   # &&
    OR_ARIT    = BinAritOperator(OR_OR)     # ||
    XOR_BOOL   = BinAritOperator(dblCaret)  # ^^
    COMMA      = BinAritOperator(comma)     # ,
    TERN_QUEST = BinAritOperator(quest)     # ?
    TERN_COLON = BinAritOperator(colon)     # :

    ASSGN          = BinAritOperator(assgn)         # =
    ADD_ASSGN      = BinAritOperator(addAssgn)      # +=
    SUB_ASSGN      = BinAritOperator(subAssgn)      # -=
    MUL_ASSGN      = BinAritOperator(mulAssgn)      # *=
    QUO_ASSGN      = BinAritOperator(quoAssgn)      # /=
    REM_ASSGN      = BinAritOperator(remAssgn)      # %=
    AND_ASSGN      = BinAritOperator(andAssgn)      # &=
    OR_ASSGN       = BinAritOperator(orAssgn)       # |=
    XOR_ASSGN      = BinAritOperator(xorAssgn)      # ^=
    SHL_ASSGN      = BinAritOperator(shlAssgn)      # <<=
    SHR_ASSGN      = BinAritOperator(shrAssgn)      # >>=
    AND_BOOL_ASSGN = BinAritOperator(andBoolAssgn)  # &&=
    OR_BOOL_ASSGN  = BinAritOperator(orBoolAssgn)   # ||=
    XOR_BOOL_ASSGN = BinAritOperator(xorBoolAssgn)  # ^^=
    POW_ASSGN      = BinAritOperator(powAssgn)      # **=
)


type UnTestOperator token

const (
    TS_EXISTS = UnTestOperator(tsExists) + iota  # -e
    TS_REG_FILE                                  # -f
    TS_DIRECT                                    # -d
    TS_CHAR_SP                                   # -c
    TS_BLCK_SP                                   # -b
    TS_NM_PIPE                                   # -p
    TS_SOCKET                                    # -S
    TS_SMB_LINK                                  # -L
    TS_STICKY                                    # -k
    TS_GID_SET                                   # -g
    TS_UID_SET                                   # -u
    TS_GRP_OWN                                   # -G
    TS_USR_OWN                                   # -O
    TS_MODIF                                     # -N
    TS_READ                                      # -r
    TS_WRITE                                     # -w
    TS_EXEC                                      # -x
    TS_NO_EMPTY                                  # -s
    TS_FD_TERM                                   # -t
    TS_EMP_STR                                   # -z
    TS_NEMP_STR                                  # -n
    TS_OPT_SET                                   # -o
    TS_VAR_SET                                   # -v
    TS_REF_VAR                                   # -R
    TS_NOT     = UnTestOperator(exclMark)        # !
    TS_PAREN   = UnTestOperator(leftParen)       # (
)


type BinTestOperator token

const (
    TS_RE_MATCH = BinTestOperator(tsReMatch) + iota  # =~
    TS_NEWER                                         # -nt
    TS_OLDER                                         # -ot
    TS_DEVINO                                        # -ef
    TS_EQL                                           # -eq
    TS_NEQ                                           # -ne
    TS_LEQ                                           # -le
    TS_GEQ                                           # -ge
    TS_LSS                                           # -lt
    TS_GTR                                           # -gt
    AND_TEST       = BinTestOperator(AND_AND)        # &&
    OR_TEST        = BinTestOperator(OR_OR)          # ||
    TS_MATCH_SHORT = BinTestOperator(assgn)          # =
    TS_MATCH       = BinTestOperator(equal)          # ==
    TS_NO_MATCH    = BinTestOperator(nequal)         # !=
    TS_BEFORE      = BinTestOperator(rdrIn)          # <
    TS_AFTER       = BinTestOperator(rdrOut)         # >
)

func (o RedirOperator) String() string    { return token(o).String() }
func (o ProcOperator) String() string     { return token(o).String() }
func (o GlobOperator) String() string     { return token(o).String() }
func (o BinCmdOperator) String() string   { return token(o).String() }
func (o CaseOperator) String() string     { return token(o).String() }
func (o ParNamesOperator) String() string { return token(o).String() }
func (o ParExpOperator) String() string   { return token(o).String() }
func (o UnAritOperator) String() string   { return token(o).String() }
func (o BinAritOperator) String() string  { return token(o).String() }
func (o UnTestOperator) String() string   { return token(o).String() }
func (o BinTestOperator) String() string  { return token(o).String() }
"""  # noqa
