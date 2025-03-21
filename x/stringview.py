"""
NOTE:
 - should work identically with str or arr storage, but str slicing will copy

TODO:
 - cached content hash
 - read-into-array - no intermediate str
  - gonna need memoryview? gotta read int BytesIO cuz dont know size (offer hint), gotta cast that to Storage
  - getincrementaldecoder
 - ofs+stride - must support stepping
 - Char as NewType?
 - how much can memoryview do for us? slicing a char-type mv is apparently not supported...
"""
import array
import dataclasses as dc
import typing as ta


Char: ta.TypeAlias = str  # len()=1 convention
Storage: ta.TypeAlias = ta.Sequence[Char]


##


@dc.dataclass(frozen=True)
class StringView:
    storage: Storage
    length: int
    stride: int
    offset: int

    #

    @ta.overload
    def __getitem__(self, index: int) -> 'StringView': ...

    @ta.overload
    def __getitem__(self, index: slice) -> 'StringView': ...

    def __getitem__(self, index):
        if isinstance(index, int):
            return StringView(
                self.storage,
                1,
                self.stride,
                (index * self.stride) + self.offset,
            )

        elif isinstance(index, slice):
            start, stop, step = index.indices(self.length)
            if step > 0:
                new_length = (stop - start + step - 1) // step
            else:
                new_length = (start - stop - step - 1) // -step
            return StringView(
                self.storage,
                max(0, new_length),
                self.stride * step,
                self.offset + (start * self.stride),
            )

        else:
            raise TypeError(index)

    def __iter__(self) -> ta.Iterator[Char]:
        return map(
            self.storage.__getitem__,
            range(self.offset, self.offset + (self.stride * self.length), self.stride),
        )

    def __reversed__(self) -> 'StringView':
        return self.__getitem__(slice(None, None, -1))

    def __len__(self) -> int:
        return self.length

    #

    def index(self, value, start=0, stop=...):
        raise TypeError

    def count(self, value):
        raise TypeError

    def __contains__(self, value):
        raise TypeError

    #

    def str(self) -> str:
        return ''.join(self)


def mut_storage(src: Storage) -> Storage:
    return array.array('u', src)


##


def _main() -> None:
    s = 'abcdefg'
    sv = StringView(s, len(s), 1, 0)
    for idx_lst in [
        [2],
        [slice(2, None)],
        [slice(2, None), 1],
        [slice(None, None, -1)],
    ]:
        o = s
        ov = sv
        for idx in idx_lst:
            o = o[idx]
            ov = ov[idx]
        assert ov.str() == o

        r = ''.join(reversed(o))
        rv = reversed(ov)
        assert rv.str() == r  # noqa


if __name__ == '__main__':
    _main()
