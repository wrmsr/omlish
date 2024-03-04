"""
Interval:
    ssize_t a;
    ssize_t b;


Token:
    string getText();
    size_t getType();
    size_t getLine();
    size_t getCharPositionInLine();
    size_t getChannel();
    size_t getTokenIndex();
    size_t getStartIndex();
    size_t getStopIndex();

    TokenSource *getTokenSource();
    CharStream *getInputStream();

    string toString();


ParseTree:
    ParseTree *parent;
    vector<ParseTree *> children;

    string getText():

    Interval getSourceInterval();

    ParseTreeType getTreeType();


ParserRuleContext : RuleContext:
    Token *start;
    Token *stop;

    exception_ptr exception;

    TerminalNode* getToken(size_t ttype, size_t i);
    vector<TerminalNode*> getTokens(size_t ttype);

    template<typename T> T* getRuleContext(size_t i);
    template<typename T> vector<T*> getRuleContexts();

    Token* getStart();
    Token* getStop();
"""
