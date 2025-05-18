# """
# https://datatracker.ietf.org/doc/html/rfc8259
# """
# import typing as ta
#
# from ..parsers import Rule as _Rule
# from .utils import load_grammar_rules
#
#
# ##
#
#
# GRAMMAR_SRC = r"""
# json-text       = ws value ws
# begin-array     = ws %x5B ws
# begin-object    = ws %x7B ws
# end-array       = ws %x5D ws
# end-object      = ws %x7D ws
# name-separator  = ws %x3A ws
# value-separator = ws %x2C ws
#
# ws = *( %x20 / %x09 / %x0A / %x0D )
#
# value = false / null / true / object / array / number / string
#
# false = %x66.61.6c.73.65
# null  = %x6e.75.6c.6c
# true  = %x74.72.75.65
#
# object = begin-object [ member *( value-separator member ) ] end-object
# member = string name-separator value
#
# array  = begin-array [ value *( value-separator value ) ] end-array
#
# number        = [ minus ] int [ frac ] [ exp ]
# decimal-point = %x2E
# digit1-9      = %x31-39
# e             = %x65 / %x45
# exp           = e [ minus / plus ] 1*DIGIT
# frac          = decimal-point 1*DIGIT
# int           = zero / ( digit1-9 *DIGIT )
# minus         = %x2D
# plus          = %x2B
# zero          = %x30
#
# string = quotation-mark *char quotation-mark
#
# ; %x22 /          ; "    quotation mark  U+0022
# ; %x5C /          ; \    reverse solidus U+005C
# ; %x2F /          ; /    solidus         U+002F
# ; %x62 /          ; b    backspace       U+0008
# ; %x66 /          ; f    form feed       U+000C
# ; %x6E /          ; n    line feed       U+000A
# ; %x72 /          ; r    carriage return U+000D
# ; %x74 /          ; t    tab             U+0009
# ; %x75 4HEXDIG )  ; uXXXX                U+XXXX
# char = unescaped / escape ( %x22 / %x5C / %x2F / %x62 / %x66 / %x6E / %x72 / %x74 / %x75 4HEXDIG )
#
# escape = %x5C
# quotation-mark = %x22
# unescaped = %x20-21 / %x23-5B / %x5D-10FFFF
# """
#
#
# @load_grammar_rules()
# class Rule(_Rule):
#     GRAMMAR: ta.ClassVar[list[str] | str] = [
#         l
#         for l_ in GRAMMAR_SRC.splitlines()
#         for l in [l_.strip()]
#         if l and not l.startswith(';')
#     ]
