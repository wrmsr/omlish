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
import enum


##


# The list of all possible tokens.
class Token(enum.StrEnum):
    ILLEGAL_TOK = '<illegal>'

    EOF_       = '<eof>'
    NEWL_      = '<newl>'
    LIT_       = '<lit>'
    LIT_WORD_  = '<lit-word>'
    LIT_REDIR_ = '<lit-redir>'

    # Token values beyond this point stringify as exact source.
    REAL_TOKEN_BOUNDARY_ = '<real-token-boundary>'

    SGL_QUOTE = "'"
    DBL_QUOTE = '"'
    BCK_QUOTE = '`'

    AND     = '&'
    AND_AND = '&&'
    OR_OR   = '||'
    OR      = '|'
    OR_AND  = '|&'

    DOLLAR         = '$'
    DOLL_SGL_QUOTE = "$'"
    DOLL_DBL_QUOTE = '$"'
    DOLL_BRACE     = '${'
    DOLL_BRACK     = '$['
    DOLL_PAREN     = '$('
    DOLL_DBL_PAREN = '$(('
    LEFT_BRACE     = '{'
    LEFT_BRACK     = '['
    DBL_LEFT_BRACK = '[['
    LEFT_PAREN     = '('
    DBL_LEFT_PAREN = '(('

    RIGHT_BRACE     = '}'
    RIGHT_BRACK     = ']'
    DBL_RIGHT_BRACK = ']]'
    RIGHT_PAREN     = ')'
    DBL_RIGHT_PAREN = '))'
    SEMICOLON       = ';'

    DBL_SEMICOLON = ';;'
    SEMI_AND      = ';&'
    DBL_SEMI_AND  = ';;&'
    SEMI_OR       = ';|'

    EXCL_MARK = '!'
    TILDE     = '~'
    ADD_ADD   = '++'
    SUB_SUB   = '--'
    STAR      = '*'
    POWER     = '**'
    EQUAL     = '=='
    NEQUAL    = '!='
    LEQUAL    = '<='
    GEQUAL    = '>='

    ADD_ASSGN      = '+='
    SUB_ASSGN      = '-='
    MUL_ASSGN      = '*='
    QUO_ASSGN      = '/='
    REM_ASSGN      = '%='
    AND_ASSGN      = '&='
    OR_ASSGN       = '|='
    XOR_ASSGN      = '^='
    SHL_ASSGN      = '<<='
    SHR_ASSGN      = '>>='
    AND_BOOL_ASSGN = '&&='
    OR_BOOL_ASSGN  = '||='
    XOR_BOOL_ASSGN = '^^='
    POW_ASSGN      = '**='

    RDR_OUT       = '>'
    APP_OUT       = '>>'
    RDR_IN        = '<'
    RDR_IN_OUT    = '<>'
    DPL_IN        = '<&'
    DPL_OUT       = '>&'
    RDR_CLOB      = '>|'
    RDR_TRUNC     = '>!'
    APP_CLOB      = '>>|'
    APP_TRUNC     = '>>!'
    HDOC          = '<<'
    DASH_HDOC     = '<<-'
    WORD_HDOC     = '<<<'
    RDR_ALL       = '&>'
    RDR_ALL_CLOB  = '&>|'
    RDR_ALL_TRUNC = '&>!'
    APP_ALL       = '&>>'
    APP_ALL_CLOB  = '&>>|'
    APP_ALL_TRUNC = '&>>!'

    CMD_IN      = '<('
    ASSGN_PAREN = '=('
    CMD_OUT     = '>('

    PLUS      = '+'
    COL_PLUS  = ':+'
    MINUS     = '-'
    COL_MINUS = ':-'
    QUEST     = '?'
    COL_QUEST = ':?'
    ASSGN     = '='
    COL_ASSGN = ':='
    PERC      = '%'
    DBL_PERC  = '%%'
    HASH      = '#'
    DBL_HASH  = '##'
    COL_HASH  = ':#'
    CARET     = '^'
    DBL_CARET = '^^'
    COMMA     = ','
    DBL_COMMA = ',,'
    AT        = '@'
    SLASH     = '/'
    DBL_SLASH = '#'
    PERIOD    = '.'
    COLON     = ':'

    TS_EXISTS   = '-e'
    TS_REG_FILE = '-f'
    TS_DIRECT   = '-d'
    TS_CHAR_SP  = '-c'
    TS_BLCK_SP  = '-b'
    TS_NM_PIPE  = '-p'
    TS_SOCKET   = '-S'
    TS_SMB_LINK = '-L'
    TS_STICKY   = '-k'
    TS_GID_SET  = '-g'
    TS_UID_SET  = '-u'
    TS_GRP_OWN  = '-G'
    TS_USR_OWN  = '-O'
    TS_MODIF    = '-N'
    TS_READ     = '-r'
    TS_WRITE    = '-w'
    TS_EXEC     = '-x'
    TS_NO_EMPTY = '-s'
    TS_FD_TERM  = '-t'
    TS_EMP_STR  = '-z'
    TS_NEMP_STR = '-n'
    TS_OPT_SET  = '-o'
    TS_VAR_SET  = '-v'
    TS_REF_VAR  = '-R'

    TS_RE_MATCH = '=~'
    TS_NEWER    = '-nt'
    TS_OLDER    = '-ot'
    TS_DEV_INO  = '-ef'
    TS_EQL      = '-eq'
    TS_NEQ      = '-ne'
    TS_LEQ      = '-le'
    TS_GEQ      = '-ge'
    TS_LSS      = '-lt'
    TS_GTR      = '-gt'

    GLOB_QUEST = '?('
    GLOB_STAR  = '*('
    GLOB_PLUS  = '+('
    GLOB_AT    = '@('
    GLOB_EXCL  = '!('


class RedirOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    RDR_OUT       = Token.RDR_OUT
    APP_OUT       = Token.APP_OUT
    RDR_IN        = Token.RDR_IN
    RDR_IN_OUT    = Token.RDR_IN_OUT
    DPL_IN        = Token.DPL_IN
    DPL_OUT       = Token.DPL_OUT
    RDR_CLOB      = Token.RDR_CLOB
    RDR_TRUNC     = Token.RDR_TRUNC      # with [LANG_ZSH]
    APP_CLOB      = Token.APP_CLOB       # with [LANG_ZSH]
    APP_TRUNC     = Token.APP_TRUNC      # with [LANG_ZSH]
    HDOC          = Token.HDOC
    DASH_HDOC     = Token.DASH_HDOC
    WORD_HDOC     = Token.WORD_HDOC
    RDR_ALL       = Token.RDR_ALL
    RDR_ALL_CLOB  = Token.RDR_ALL_CLOB   # with [LANG_ZSH]
    RDR_ALL_TRUNC = Token.RDR_ALL_TRUNC  # with [LANG_ZSH]
    APP_ALL       = Token.APP_ALL
    APP_ALL_CLOB  = Token.APP_ALL_CLOB   # with [LANG_ZSH]
    APP_ALL_TRUNC = Token.APP_ALL_TRUNC  # with [LANG_ZSH]

    # Deprecated: use [RdrClob]
    CLB_OUT       = Token.RDR_CLOB


class ProcOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    CMD_IN      = Token.CMD_IN
    CMD_IN_TEMP = Token.ASSGN_PAREN
    CMD_OUT     = Token.CMD_OUT


class GlobOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    GLOB_ZERO_OR_ONE  = Token.GLOB_QUEST
    GLOB_ZERO_OR_MORE = Token.GLOB_STAR
    GLOB_ONE_OR_MORE  = Token.GLOB_PLUS
    GLOB_ONE          = Token.GLOB_AT
    GLOB_EXCEPT       = Token.GLOB_EXCL


class BinCmdOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    AND_STMT = Token.AND_AND
    OR_STMT  = Token.OR_OR
    PIPE     = Token.OR
    PIPE_ALL = Token.OR_AND


class CaseOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    BREAK       = Token.DBL_SEMICOLON
    FALLTHROUGH = Token.SEMI_AND
    RESUME      = Token.DBL_SEMI_AND
    RESUME_KORN = Token.SEMI_OR


class ParNamesOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    NAMES_PREFIX       = Token.STAR
    NAMES_PREFIX_WORDS = Token.AT


class ParExpOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    ALTERNATE_UNSET         = Token.PLUS
    ALTERNATE_UNSET_OR_NULL = Token.COL_PLUS 
    DEFAULT_UNSET           = Token.MINUS    
    DEFAULT_UNSET_OR_NULL   = Token.COL_MINUS
    ERROR_UNSET             = Token.QUEST    
    ERROR_UNSET_OR_NULL     = Token.COL_QUEST
    ASSIGN_UNSET            = Token.ASSGN    
    ASSIGN_UNSET_OR_NULL    = Token.COL_ASSGN
    REM_SMALL_SUFFIX        = Token.PERC     
    REM_LARGE_SUFFIX        = Token.DBL_PERC 
    REM_SMALL_PREFIX        = Token.HASH     
    REM_LARGE_PREFIX        = Token.DBL_HASH 
    MATCH_EMPTY             = Token.COL_HASH 
    UPPER_FIRST             = Token.CARET    
    UPPER_ALL               = Token.DBL_CARET
    LOWER_FIRST             = Token.COMMA    
    LOWER_ALL               = Token.DBL_COMMA
    OTHER_PARAMOPS          = Token.AT       


class UnAritOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    NOT          = Token.EXCL_MARK
    BIT_NEGATION = Token.TILDE
    INC          = Token.ADD_ADD
    DEC          = Token.SUB_SUB
    PLUS         = Token.PLUS
    MINUS        = Token.MINUS


class BinAritOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    ADD = Token.PLUS
    SUB = Token.MINUS
    MUL = Token.STAR
    QUO = Token.SLASH
    REM = Token.PERC
    POW = Token.POWER
    EQL = Token.EQUAL
    GTR = Token.RDR_OUT
    LSS = Token.RDR_IN
    NEQ = Token.NEQUAL
    LEQ = Token.LEQUAL
    GEQ = Token.GEQUAL
    AND = Token.AND
    OR  = Token.OR
    XOR = Token.CARET
    SHR = Token.APP_OUT
    SHL = Token.HDOC

    # TODO: use "Bool" consistently for logical operators like AndArit and OrArit; use #go:fix inline?

    AND_ARIT   = Token.AND_AND
    OR_ARIT    = Token.OR_OR
    XOR_BOOL   = Token.DBL_CARET
    COMMA      = Token.COMMA
    TERN_QUEST = Token.QUEST
    TERN_COLON = Token.COLON

    ASSGN          = Token.ASSGN
    ADD_ASSGN      = Token.ADD_ASSGN
    SUB_ASSGN      = Token.SUB_ASSGN
    MUL_ASSGN      = Token.MUL_ASSGN
    QUO_ASSGN      = Token.QUO_ASSGN
    REM_ASSGN      = Token.REM_ASSGN
    AND_ASSGN      = Token.AND_ASSGN
    OR_ASSGN       = Token.OR_ASSGN
    XOR_ASSGN      = Token.XOR_ASSGN
    SHL_ASSGN      = Token.SHL_ASSGN
    SHR_ASSGN      = Token.SHR_ASSGN
    AND_BOOL_ASSGN = Token.AND_BOOL_ASSGN
    OR_BOOL_ASSGN  = Token.OR_BOOL_ASSGN
    XOR_BOOL_ASSGN = Token.XOR_BOOL_ASSGN
    POW_ASSGN      = Token.POW_ASSGN


class UnTestOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    TS_EXISTS   = Token.TS_EXISTS
    TS_REG_FILE = Token.TS_REG_FILE
    TS_DIRECT   = Token.TS_DIRECT
    TS_CHAR_SP  = Token.TS_CHAR_SP
    TS_BLCK_SP  = Token.TS_BLCK_SP
    TS_NM_PIPE  = Token.TS_NM_PIPE
    TS_SOCKET   = Token.TS_SOCKET
    TS_SMB_LINK = Token.TS_SMB_LINK
    TS_STICKY   = Token.TS_STICKY
    TS_GID_SET  = Token.TS_GID_SET
    TS_UID_SET  = Token.TS_UID_SET
    TS_GRP_OWN  = Token.TS_GRP_OWN
    TS_USR_OWN  = Token.TS_USR_OWN
    TS_MODIF    = Token.TS_MODIF
    TS_READ     = Token.TS_READ
    TS_WRITE    = Token.TS_WRITE
    TS_EXEC     = Token.TS_EXEC
    TS_NO_EMPTY = Token.TS_NO_EMPTY
    TS_FD_TERM  = Token.TS_FD_TERM
    TS_EMP_STR  = Token.TS_EMP_STR
    TS_NEMP_STR = Token.TS_NEMP_STR
    TS_OPT_SET  = Token.TS_OPT_SET
    TS_VAR_SET  = Token.TS_VAR_SET
    TS_REF_VAR  = Token.TS_REF_VAR
    TS_NOT      = Token.EXCL_MARK
    TS_PAREN    = Token.LEFT_PAREN


class BinTestOperator(enum.Enum):
    def string(self) -> str:
        return self.value.value  # noqa

    TS_RE_MATCH    = Token.TS_RE_MATCH
    TS_NEWER       = Token.TS_NEWER
    TS_OLDER       = Token.TS_OLDER
    TS_DEV_INO     = Token.TS_DEV_INO
    TS_EQL         = Token.TS_EQL
    TS_NEQ         = Token.TS_NEQ
    TS_LEQ         = Token.TS_LEQ
    TS_GEQ         = Token.TS_GEQ
    TS_LSS         = Token.TS_LSS
    TS_GTR         = Token.TS_GTR
    AND_TEST       = Token.AND_AND
    OR_TEST        = Token.OR_OR
    TS_MATCH_SHORT = Token.ASSGN
    TS_MATCH       = Token.EQUAL
    TS_NO_MATCH    = Token.NEQUAL
    TS_BEFORE      = Token.RDR_IN
    TS_AFTER       = Token.RDR_OUT
