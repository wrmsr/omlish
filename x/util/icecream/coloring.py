"""
IceCream - Never use print() to debug again

Ansgar Grunseid
grunseid.com
grunseid@gmail.com

License: MIT
"""
import typing as ta

import pygments.style
import pygments.token as pt


# Solarized: https://ethanschoonover.com/solarized/
class SolarizedDark(pygments.style.Style):

    BASE03  = '#002b36' # noqa
    BASE02  = '#073642' # noqa
    BASE01  = '#586e75' # noqa
    BASE00  = '#657b83' # noqa
    BASE0   = '#839496' # noqa
    BASE1   = '#93a1a1' # noqa
    BASE2   = '#eee8d5' # noqa
    BASE3   = '#fdf6e3' # noqa
    YELLOW  = '#b58900' # noqa
    ORANGE  = '#cb4b16' # noqa
    RED     = '#dc322f' # noqa
    MAGENTA = '#d33682' # noqa
    VIOLET  = '#6c71c4' # noqa
    BLUE    = '#268bd2' # noqa
    CYAN    = '#2aa198' # noqa
    GREEN   = '#859900' # noqa

    styles: ta.ClassVar = {
        pt.Text:                   BASE0,
        pt.Whitespace:             BASE03,
        pt.Error:                  RED,
        pt.Other:                  BASE0,

        pt.Name:                   BASE1,
        pt.Name.Attribute:         BASE0,
        pt.Name.Builtin:           BLUE,
        pt.Name.Builtin.Pseudo:    BLUE,
        pt.Name.Class:             BLUE,
        pt.Name.Constant:          YELLOW,
        pt.Name.Decorator:         ORANGE,
        pt.Name.Entity:            ORANGE,
        pt.Name.Exception:         ORANGE,
        pt.Name.Function:          BLUE,
        pt.Name.Property:          BLUE,
        pt.Name.Label:             BASE0,
        pt.Name.Namespace:         YELLOW,
        pt.Name.Other:             BASE0,
        pt.Name.Tag:               GREEN,
        pt.Name.Variable:          ORANGE,
        pt.Name.Variable.Class:    BLUE,
        pt.Name.Variable.Global:   BLUE,
        pt.Name.Variable.Instance: BLUE,

        pt.String:                 CYAN,
        pt.String.Backtick:        CYAN,
        pt.String.Char:            CYAN,
        pt.String.Doc:             CYAN,
        pt.String.Double:          CYAN,
        pt.String.Escape:          ORANGE,
        pt.String.Heredoc:         CYAN,
        pt.String.Interpol:        ORANGE,
        pt.String.Other:           CYAN,
        pt.String.Regex:           CYAN,
        pt.String.Single:          CYAN,
        pt.String.Symbol:          CYAN,

        pt.Number:                 CYAN,
        pt.Number.Float:           CYAN,
        pt.Number.Hex:             CYAN,
        pt.Number.Integer:         CYAN,
        pt.Number.Integer.Long:    CYAN,
        pt.Number.Oct:             CYAN,

        pt.Keyword:                GREEN,
        pt.Keyword.Constant:       GREEN,
        pt.Keyword.Declaration:    GREEN,
        pt.Keyword.Namespace:      ORANGE,
        pt.Keyword.Pseudo:         ORANGE,
        pt.Keyword.Reserved:       GREEN,
        pt.Keyword.Type:           GREEN,

        pt.Generic:                BASE0,
        pt.Generic.Deleted:        BASE0,
        pt.Generic.Emph:           BASE0,
        pt.Generic.Error:          BASE0,
        pt.Generic.Heading:        BASE0,
        pt.Generic.Inserted:       BASE0,
        pt.Generic.Output:         BASE0,
        pt.Generic.Prompt:         BASE0,
        pt.Generic.Strong:         BASE0,
        pt.Generic.Subheading:     BASE0,
        pt.Generic.Traceback:      BASE0,

        pt.Literal:                BASE0,
        pt.Literal.Date:           BASE0,

        pt.Comment:                BASE01,
        pt.Comment.Multiline:      BASE01,
        pt.Comment.Preproc:        BASE01,
        pt.Comment.Single:         BASE01,
        pt.Comment.Special:        BASE01,

        pt.Operator:               BASE0,
        pt.Operator.Word:          GREEN,

        pt.Punctuation:            BASE0,
    }
