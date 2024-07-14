import abc
import typing as ta

from ... import lang


MutationReason = ta.Any


class EvalContext(lang.Abstract):

    @abc.abstractmethod
    def get_var(self, name: str) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def set_var(
            self,
            name: str,
            val: ta.Any,
            mutation_reason: ta.Optional[MutationReason] = None,
    ) -> 'EvalContext':
        raise NotImplementedError


class MutableEvalContext(EvalContext):

    def __init__(self, vars: ta.Optional[ta.Mapping[str, ta.Any]] = None) -> None:
        super().__init__()
        self._vars = vars if vars is not None else None

    def get_var(self, name: str) -> ta.Any:
        return self._vars[name]

    def set_var(
            self,
            name: str,
            val: ta.Any,
            mutation_reason: ta.Optional[MutationReason] = None,
    ) -> 'MutableEvalContext':
        self._vars[name] = val
        return self


class ImmutableEvalContext(EvalContext):

    def __init__(
            self,
            vars: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> None:
        super().__init__()
        self._vars = dict(vars or [])

    def get_var(self, name: str) -> ta.Any:
        return self._vars[name]

    def set_var(
            self,
            name: str,
            val: ta.Any,
            mutation_reason: ta.Optional[MutationReason] = None,
    ) -> 'ImmutableEvalContext':
        return type(self)({**self._vars, name: val})


class TrackingImmutableEvalContext(ImmutableEvalContext):

    def __init__(
            self,
            vars: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            *,
            parent: ta.Optional['TrackingImmutableEvalContext'] = None,
            mutation_reason: ta.Any = None,
    ) -> None:
        super().__init__()
        self._vars = dict(vars or [])
        self._parent = parent
        self._reason = mutation_reason

    def set_var(
            self,
            name: str,
            val: ta.Any,
            mutation_reason: ta.Optional[MutationReason] = None,
    ) -> 'TrackingImmutableEvalContext':
        return type(self)(
            {**self._vars, name: val},
            parent=self,
            mutation_reason=mutation_reason,
        )
