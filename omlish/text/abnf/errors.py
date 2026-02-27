class AbnfError(Exception):
    pass


class AbnfIncompleteParseError(AbnfError):
    pass


class AbnfGrammarParseError(AbnfError):
    pass
