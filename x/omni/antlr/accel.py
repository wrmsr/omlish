"""
from ..antlr import _accel
from .._vendor.antlr4.PredictionContext import PredictionContextCache
lexer._interp = _accel.LexerATNSimulator(lexer, lexer.atn, lexer.decisionsToDFA, PredictionContextCache())
lexer.decisionsToDFA = lexer._interp.decisionToDFA
"""
import logging
import typing as ta


T = ta.TypeVar('T')


log = logging.getLogger(__name__)
