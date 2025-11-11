import dataclasses as dc

from omlish import check

from ...py.tokens import all as tks


##


TYPE_ALIAS_COMMENT = '# ta.TypeAlias'
NOQA_TYPE_ALIAS_COMMENT = TYPE_ALIAS_COMMENT + '  # noqa'

NO_MOVE_COMMENT = '# omlish-amalg-typing-no-move'


@dc.dataclass(frozen=True, kw_only=True)
class Typing:
    src: str

    src_path: str
    line: int

    toks: tks.Tokens = dc.field(repr=False)


def _is_typing(
        lts: tks.Tokens,
        *,
        exclude_newtypes: bool = False,
) -> bool:
    es = tks.join_toks(lts).strip()
    if es.endswith(NO_MOVE_COMMENT):
        return False
    if any(es.endswith(sfx) for sfx in (TYPE_ALIAS_COMMENT, NOQA_TYPE_ALIAS_COMMENT)):
        return True

    wts = list(tks.ignore_ws(lts, keep=['INDENT', 'UNINDENT']))
    if not tks.match_toks(wts, [
        ('NAME', None),
        ('OP', '='),
        ('NAME', 'ta'),
        ('OP', '.'),
        (None, None),
    ]):
        return False

    if exclude_newtypes:
        if wts[4].name == 'NAME' and wts[4].src == 'NewType':
            return False

    return True


def make_typing(
        lts: tks.Tokens,
        *,
        src_path: str,
) -> Typing | None:
    if not lts or lts[0].name == 'UNIMPORTANT_WS':
        return None

    if not _is_typing(lts, exclude_newtypes=True):
        return None

    ft = next(iter(tks.ignore_ws(lts)))
    return Typing(
        src=tks.join_toks(lts),

        src_path=src_path,
        line=check.not_none(ft.line),

        toks=lts,
    )


##


def is_root_level_if_type_checking_block(lts: tks.Tokens) -> bool:
    return tks.match_toks(tks.ignore_ws(lts, keep=['INDENT']), [
        ('NAME', 'if'),
        ('NAME', 'ta'),
        ('OP', '.'),
        ('NAME', 'TYPE_CHECKING'),
        ('OP', ':'),
    ])


def skip_root_level_if_type_checking_block(
        cls: list[tks.Tokens],
        i: int,
) -> int:
    def skip_block():
        nonlocal i

        nl = cls[i]
        if nl[0].name != 'INDENT':
            raise RuntimeError
        i += 1

        while True:
            nl = cls[i]
            if nl and nl[0].name == 'DEDENT':
                return nl
            i += 1

    nl = skip_block()

    if tks.match_toks(nl, [
        ('DEDENT', None),
        ('NAME', 'else'),
    ]):
        i += 1
        skip_block()

    return i
