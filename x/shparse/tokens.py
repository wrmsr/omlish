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
package syntax

//go:generate go tool stringer -type token -linecomment -trimprefix _

type token uint32

// The list of all possible tokens.
const (
	illegalTok token = iota

	_EOF
	_Newl
	_Lit
	_LitWord
	_LitRedir

	// Token values beyond this point stringify as exact source.
	_realTokenBoundary

	sglQuote // '
	dblQuote // "
	bckQuote // `

	and    // &
	andAnd // &&
	orOr   // ||
	or     // |
	orAnd  // |&

	dollar       // $
	dollSglQuote // $'
	dollDblQuote // $"
	dollBrace    // ${
	dollBrack    // $[
	dollParen    // $(
	dollDblParen // $((
	leftBrace    // {
	leftBrack    // [
	dblLeftBrack // [[
	leftParen    // (
	dblLeftParen // ((

	rightBrace    // }
	rightBrack    // ]
	dblRightBrack // ]]
	rightParen    // )
	dblRightParen // ))
	semicolon     // ;

	dblSemicolon // ;;
	semiAnd      // ;&
	dblSemiAnd   // ;;&
	semiOr       // ;|

	exclMark // !
	tilde    // ~
	addAdd   // ++
	subSub   // --
	star     // *
	power    // **
	equal    // ==
	nequal   // !=
	lequal   // <=
	gequal   // >=

	addAssgn     // +=
	subAssgn     // -=
	mulAssgn     // *=
	quoAssgn     // /=
	remAssgn     // %=
	andAssgn     // &=
	orAssgn      // |=
	xorAssgn     // ^=
	shlAssgn     // <<=
	shrAssgn     // >>=
	andBoolAssgn // &&=
	orBoolAssgn  // ||=
	xorBoolAssgn // ^^=
	powAssgn     // **=

	rdrOut      // >
	appOut      // >>
	rdrIn       // <
	rdrInOut    // <>
	dplIn       // <&
	dplOut      // >&
	rdrClob     // >|
	rdrTrunc    // >!
	appClob     // >>|
	appTrunc    // >>!
	hdoc        // <<
	dashHdoc    // <<-
	wordHdoc    // <<<
	rdrAll      // &>
	rdrAllClob  // &>|
	rdrAllTrunc // &>!
	appAll      // &>>
	appAllClob  // &>>|
	appAllTrunc // &>>!

	cmdIn      // <(
	assgnParen // =(
	cmdOut     // >(

	plus     // +
	colPlus  // :+
	minus    // -
	colMinus // :-
	quest    // ?
	colQuest // :?
	assgn    // =
	colAssgn // :=
	perc     // %
	dblPerc  // %%
	hash     // #
	dblHash  // ##
	colHash  // :#
	caret    // ^
	dblCaret // ^^
	comma    // ,
	dblComma // ,,
	at       // @
	slash    // /
	dblSlash // //
	period   // .
	colon    // :

	tsExists  // -e
	tsRegFile // -f
	tsDirect  // -d
	tsCharSp  // -c
	tsBlckSp  // -b
	tsNmPipe  // -p
	tsSocket  // -S
	tsSmbLink // -L
	tsSticky  // -k
	tsGIDSet  // -g
	tsUIDSet  // -u
	tsGrpOwn  // -G
	tsUsrOwn  // -O
	tsModif   // -N
	tsRead    // -r
	tsWrite   // -w
	tsExec    // -x
	tsNoEmpty // -s
	tsFdTerm  // -t
	tsEmpStr  // -z
	tsNempStr // -n
	tsOptSet  // -o
	tsVarSet  // -v
	tsRefVar  // -R

	tsReMatch // =~
	tsNewer   // -nt
	tsOlder   // -ot
	tsDevIno  // -ef
	tsEql     // -eq
	tsNeq     // -ne
	tsLeq     // -le
	tsGeq     // -ge
	tsLss     // -lt
	tsGtr     // -gt

	globQuest // ?(
	globStar  // *(
	globPlus  // +(
	globAt    // @(
	globExcl  // !(
)

type RedirOperator token

const (
	RdrOut      = RedirOperator(rdrOut) + iota // >
	AppOut                                     // >>
	RdrIn                                      // <
	RdrInOut                                   // <>
	DplIn                                      // <&
	DplOut                                     // >&
	RdrClob                                    // >|
	RdrTrunc                                   // >! with [LangZsh]
	AppClob                                    // >>| with [LangZsh]
	AppTrunc                                   // >>! with [LangZsh]
	Hdoc                                       // <<
	DashHdoc                                   // <<-
	WordHdoc                                   // <<<
	RdrAll                                     // &>
	RdrAllClob                                 // &>| with [LangZsh]
	RdrAllTrunc                                // &>! with [LangZsh]
	AppAll                                     // &>>
	AppAllClob                                 // &>>| with [LangZsh]
	AppAllTrunc                                // &>>! with [LangZsh]

	// Deprecated: use [RdrClob]
	//
	//go:fix inline
	ClbOut = RdrClob
)

type ProcOperator token

const (
	CmdIn     = ProcOperator(cmdIn) + iota // <(
	CmdInTemp                              // =(
	CmdOut                                 // >(
)

type GlobOperator token

const (
	GlobZeroOrOne  = GlobOperator(globQuest) + iota // ?(
	GlobZeroOrMore                                  // *(
	GlobOneOrMore                                   // +(
	GlobOne                                         // @(
	GlobExcept                                      // !(
)

type BinCmdOperator token

const (
	AndStmt = BinCmdOperator(andAnd) + iota // &&
	OrStmt                                  // ||
	Pipe                                    // |
	PipeAll                                 // |&
)

type CaseOperator token

const (
	Break       = CaseOperator(dblSemicolon) + iota // ;;
	Fallthrough                                     // ;&
	Resume                                          // ;;&
	ResumeKorn                                      // ;|
)

type ParNamesOperator token

const (
	NamesPrefix      = ParNamesOperator(star) // *
	NamesPrefixWords = ParNamesOperator(at)   // @
)

type ParExpOperator token

const (
	AlternateUnset       = ParExpOperator(plus) + iota // +
	AlternateUnsetOrNull                               // :+
	DefaultUnset                                       // -
	DefaultUnsetOrNull                                 // :-
	ErrorUnset                                         // ?
	ErrorUnsetOrNull                                   // :?
	AssignUnset                                        // =
	AssignUnsetOrNull                                  // :=
	RemSmallSuffix                                     // %
	RemLargeSuffix                                     // %%
	RemSmallPrefix                                     // #
	RemLargePrefix                                     // ##
	MatchEmpty                                         // :# with [LangZsh]
	UpperFirst                                         // ^
	UpperAll                                           // ^^
	LowerFirst                                         // ,
	LowerAll                                           // ,,
	OtherParamOps                                      // @
)

type UnAritOperator token

const (
	Not         = UnAritOperator(exclMark) + iota // !
	BitNegation                                   // ~
	Inc                                           // ++
	Dec                                           // --
	Plus        = UnAritOperator(plus)            // +
	Minus       = UnAritOperator(minus)           // -
)

type BinAritOperator token

const (
	Add = BinAritOperator(plus)   // +
	Sub = BinAritOperator(minus)  // -
	Mul = BinAritOperator(star)   // *
	Quo = BinAritOperator(slash)  // /
	Rem = BinAritOperator(perc)   // %
	Pow = BinAritOperator(power)  // **
	Eql = BinAritOperator(equal)  // ==
	Gtr = BinAritOperator(rdrOut) // >
	Lss = BinAritOperator(rdrIn)  // <
	Neq = BinAritOperator(nequal) // !=
	Leq = BinAritOperator(lequal) // <=
	Geq = BinAritOperator(gequal) // >=
	And = BinAritOperator(and)    // &
	Or  = BinAritOperator(or)     // |
	Xor = BinAritOperator(caret)  // ^
	Shr = BinAritOperator(appOut) // >>
	Shl = BinAritOperator(hdoc)   // <<

	// TODO: use "Bool" consistently for logical operators like AndArit and OrArit; use //go:fix inline?

	AndArit   = BinAritOperator(andAnd)   // &&
	OrArit    = BinAritOperator(orOr)     // ||
	XorBool   = BinAritOperator(dblCaret) // ^^
	Comma     = BinAritOperator(comma)    // ,
	TernQuest = BinAritOperator(quest)    // ?
	TernColon = BinAritOperator(colon)    // :

	Assgn        = BinAritOperator(assgn)        // =
	AddAssgn     = BinAritOperator(addAssgn)     // +=
	SubAssgn     = BinAritOperator(subAssgn)     // -=
	MulAssgn     = BinAritOperator(mulAssgn)     // *=
	QuoAssgn     = BinAritOperator(quoAssgn)     // /=
	RemAssgn     = BinAritOperator(remAssgn)     // %=
	AndAssgn     = BinAritOperator(andAssgn)     // &=
	OrAssgn      = BinAritOperator(orAssgn)      // |=
	XorAssgn     = BinAritOperator(xorAssgn)     // ^=
	ShlAssgn     = BinAritOperator(shlAssgn)     // <<=
	ShrAssgn     = BinAritOperator(shrAssgn)     // >>=
	AndBoolAssgn = BinAritOperator(andBoolAssgn) // &&=
	OrBoolAssgn  = BinAritOperator(orBoolAssgn)  // ||=
	XorBoolAssgn = BinAritOperator(xorBoolAssgn) // ^^=
	PowAssgn     = BinAritOperator(powAssgn)     // **=
)

type UnTestOperator token

const (
	TsExists  = UnTestOperator(tsExists) + iota // -e
	TsRegFile                                   // -f
	TsDirect                                    // -d
	TsCharSp                                    // -c
	TsBlckSp                                    // -b
	TsNmPipe                                    // -p
	TsSocket                                    // -S
	TsSmbLink                                   // -L
	TsSticky                                    // -k
	TsGIDSet                                    // -g
	TsUIDSet                                    // -u
	TsGrpOwn                                    // -G
	TsUsrOwn                                    // -O
	TsModif                                     // -N
	TsRead                                      // -r
	TsWrite                                     // -w
	TsExec                                      // -x
	TsNoEmpty                                   // -s
	TsFdTerm                                    // -t
	TsEmpStr                                    // -z
	TsNempStr                                   // -n
	TsOptSet                                    // -o
	TsVarSet                                    // -v
	TsRefVar                                    // -R
	TsNot     = UnTestOperator(exclMark)        // !
	TsParen   = UnTestOperator(leftParen)       // (
)

type BinTestOperator token

const (
	TsReMatch    = BinTestOperator(tsReMatch) + iota // =~
	TsNewer                                          // -nt
	TsOlder                                          // -ot
	TsDevIno                                         // -ef
	TsEql                                            // -eq
	TsNeq                                            // -ne
	TsLeq                                            // -le
	TsGeq                                            // -ge
	TsLss                                            // -lt
	TsGtr                                            // -gt
	AndTest      = BinTestOperator(andAnd)           // &&
	OrTest       = BinTestOperator(orOr)             // ||
	TsMatchShort = BinTestOperator(assgn)            // =
	TsMatch      = BinTestOperator(equal)            // ==
	TsNoMatch    = BinTestOperator(nequal)           // !=
	TsBefore     = BinTestOperator(rdrIn)            // <
	TsAfter      = BinTestOperator(rdrOut)           // >
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
