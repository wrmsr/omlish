import typing as ta

from omlish import check
from omlish import lang

from .types import Token
from .types import TokenStr


##


class NotSeqVocabError(Exception):
    pass


class Vocab(lang.Final):
    def __init__(
            self,
            tups: ta.Iterable[tuple[Token, TokenStr]],
    ) -> None:
        super().__init__()

        check.not_isinstance(tups, tuple)

        tok_str_by_tok: dict[Token, TokenStr] = {}
        tok_by_tok_str: dict[TokenStr, Token] = {}
        for tok, tok_str in tups:
            check.isinstance(tok, int)
            check.isinstance(tok_str, TokenStr)
            check.not_in(tok, tok_str_by_tok)
            check.not_in(tok_str, tok_by_tok_str)
            tok_str_by_tok[tok] = tok_str
            tok_by_tok_str[tok_str] = tok

        self._tok_str_by_tok = tok_str_by_tok
        self._tok_by_tok_str = tok_by_tok_str

        self._min_tok = min(tok_str_by_tok)
        self._max_tok = max(tok_str_by_tok)

        self._is_dense = ta.cast('set[int]', set(tok_str_by_tok)) == set(range(self._min_tok, self._max_tok + 1))

        self._is_seq = self._is_dense and 0 in tok_str_by_tok
        if self._is_seq:
            self._seq = [
                ts
                for _, ts in sorted(
                    tok_str_by_tok.items(),
                    key=lambda t_ts: t_ts[0],
                )
            ]

    _seq: ta.Sequence[TokenStr]

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<len={len(self._tok_str_by_tok)}>'

    #

    @property
    def tok_str_by_tok(self) -> ta.Mapping[Token, TokenStr]:
        return self._tok_str_by_tok

    @property
    def tok_by_tok_str(self) -> ta.Mapping[TokenStr, Token]:
        return self._tok_by_tok_str

    @property
    def min_tok(self) -> Token:
        return self._min_tok

    @property
    def max_tok(self) -> Token:
        return self._max_tok

    @property
    def is_dense(self) -> bool:
        return self._is_dense

    @property
    def is_seq(self) -> bool:
        return self._is_seq

    @property
    def seq(self) -> ta.Sequence[TokenStr]:
        try:
            return self._seq
        except AttributeError:
            raise NotSeqVocabError(self) from None

    #

    def __len__(self) -> int:
        return len(self._tok_str_by_tok)

    def __iter__(self) -> ta.Iterator[tuple[Token, TokenStr]]:
        return iter(self._tok_str_by_tok.items())

    @ta.overload
    def __getitem__(self, item: Token) -> TokenStr:
        ...

    @ta.overload
    def __getitem__(self, item: TokenStr) -> Token:
        ...

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._tok_str_by_tok[ta.cast(Token, item)]
        elif isinstance(item, TokenStr):
            return self._tok_by_tok_str[item]
        else:
            raise TypeError(item)

    @ta.overload
    def get(self, item: Token, default: TokenStr) -> TokenStr:
        ...

    @ta.overload
    def get(self, item: Token, default: TokenStr | None = None) -> TokenStr | None:
        ...

    @ta.overload
    def get(self, item: TokenStr, default: Token) -> Token:
        ...

    @ta.overload
    def get(self, item: TokenStr, default: Token | None = None) -> Token | None:
        ...

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def __contains__(self, item: Token | TokenStr) -> bool:
        if isinstance(item, int):
            return item in self._tok_str_by_tok
        elif isinstance(item, TokenStr):
            return item in self._tok_by_tok_str
        else:
            raise TypeError(item)
