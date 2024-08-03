import typing as ta


V = ta.TypeVar('V')


class HttpMap(ta.Mapping[str, V]):
    def __getitem__(self, k):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError
