- upsert
  ```sql
  insert into vocabulary(word) values('jovial') on conflict(word) do update set count=count+1;
  ```
- subquery relation
- binary
  - in_
  - like
    - no this is a dedicated node, escape / negation in grammar
- exprs
  - case
  - cast / ::
  - explicit null? already wrapped in non-null Literal node
- rendering
  - minimal parens / needs_parens
    ```python
    def needs_parens(self, e: Expr) -> bool:
        if isinstance(e, (Literal, Ident, Name)):
            return True
        elif isinstance(e, Expr):
            return False
        else:
            raise TypeError(e)
    ```
  - text.parts
  - QuoteStyle
  - ParamStyle
- literal rendering
    - unparameterized style, 'quote style'?
    - more safe literal types
