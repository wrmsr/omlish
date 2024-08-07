import importlib.resources
import typing as ta

from omlish import cached
from omlish import check
from omlish import defs
from omlish import lang

from .rand import Gen
from .rand import GenRandom
from .rand import IntGen


class TextDist:

    def __init__(self, name: str, weights_by_value: ta.Mapping[str, int]) -> None:
        super().__init__()

        self._name = check.not_none(name)
        self._values: ta.List[str] = []
        self._weights = [0] * len(weights_by_value)

        running_weight = 0
        is_valid = True
        for i, (k, v) in enumerate(weights_by_value.items()):
            self._values.append(k)
            running_weight += v
            self._weights[i] = running_weight
            is_valid &= v > 0

        #  "nations" is hack and not a valid dist so we need to skip it
        if is_valid:
            self._max_weight = self._weights[-1]
            self._seq: list[str | None] = [None] * self._max_weight
            self._bytes_seq: list[bytes | None] = [None] * self._max_weight

            i = 0
            for value in self._values:
                bytes_value = value.encode('utf-8')
                check.state(len(bytes_value) == len(value))
                for _ in range(weights_by_value[value]):
                    self._seq[i] = value
                    self._bytes_seq[i] = bytes_value
                    i += 1

        else:
            self._max_weight = -1
            self._seq = None
            self._bytes_seq = None

    defs.getter('name')
    defs.repr('name')

    @property
    def values(self) -> ta.Sequence[str]:
        return self._values

    @property
    def weights(self) -> ta.Sequence[int]:
        return self._weights

    @property
    def size(self) -> int:
        return len(self._values)

    @property
    def seq(self) -> ta.Sequence[str]:
        return self._seq

    @property
    def bytes_seq(self) -> ta.Sequence[bytes]:
        return self._bytes_seq

    def random_value(self, gen: Gen) -> str:
        if self._seq is None:
            raise ValueError(self._seq)
        random_value = gen.rand(0, self._max_weight - 1)
        return self._seq[random_value]

    def random_bytes_value(self, gen: Gen) -> bytes:
        if self._seq is None:
            raise ValueError(self._seq)
        random_value = gen.rand(0, self._max_weight - 1)
        return self._bytes_seq[random_value]


class RandomString(GenRandom):

    def __init__(self, seed: int, dist: TextDist, expected_row_count: int = 1) -> None:
        super().__init__(IntGen(seed, expected_row_count))

        self._dist = dist

    def next_value(self) -> str:
        return self._dist.random_value(self._gen)


class RandomStringSequence(GenRandom):

    def __init__(self, seed: int, count: int, dist: TextDist, expected_row_count: int = 1) -> None:
        super().__init__(IntGen(seed, dist.size * expected_row_count))

        self._count = count
        self._dist = dist

    def next_value(self) -> str:
        values = list(self._dist.values)
        check.arg(self._count < len(values))

        # randomize first 'count' elements of the string
        for current_position in range(self._count):
            swap_position = self._gen.rand(current_position, len(values) - 1)
            values[current_position], values[swap_position] = values[swap_position], values[current_position]

        return ' '.join(values[:self._count])


class TextDistLoading:

    @classmethod
    def load_dist(cls, buf: str) -> ta.Mapping[str, TextDist]:
        return cls._load_dists((
            l
            for l in buf.splitlines()
            for l in [l.strip()]
            if not l.startswith('#')
        ))

    @classmethod
    def _load_dists(cls, lines: ta.Iterable[str]) -> ta.Mapping[str, TextDist]:
        dists: ta.Dict[str, TextDist] = {}

        lines = iter(lines)
        while True:
            line = next(lines, None)
            if line is None:
                break

            parts = line.strip().split()
            if len(parts) != 2:
                continue

            if parts[0].upper() == 'BEGIN':
                name = parts[1]
                dist = cls._load_dist(lines, name)
                dists[name.lower()] = dist

        return dists

    @classmethod
    def _load_dist(cls, lines: ta.Iterator[str], name: str) -> TextDist:
        count = -1
        members: ta.Dict[str, int] = {}
        while True:
            line = next(lines, None)
            if line is None:
                break

            if cls._is_end(name, line):
                weights = dict(members)
                check.state(count == len(weights))
                return TextDist(name, weights)

            parts = [p for p in line.strip().split('|') for p in [p.strip()] if p]
            check.state(len(parts) == 2)

            value = parts[0]
            weight = int(parts[1])

            if value.lower() == 'count':
                count = weight
            else:
                members[value] = weight

        raise ValueError(name)

    @classmethod
    def _is_end(cls, name: str, line: str) -> bool:
        parts = [p for p in line.strip().split() for p in [p.strip()] if p]
        if parts[0].upper() == 'END':
            check.state(len(parts) == 2 and parts[1].lower() == name.lower())
            return True
        return False


class TextDists:

    def __init__(self, dists_by_name: ta.Mapping[str, TextDist]) -> None:
        super().__init__()

        self._dists_by_name = dists_by_name

    @cached.function
    @classmethod
    def default(cls) -> 'TextDists':
        src = importlib.resources.files(__package__).joinpath('dists.dss').read_text()
        data = TextDistLoading.load_dist(src)
        return cls(data)

    def __getitem__(self, name: str) -> TextDist:
        return self._dists_by_name[name]

    grammars: TextDist = lang.item_property('grammar')
    noun_phrase: TextDist = lang.item_property('np')
    verb_phrase: TextDist = lang.item_property('vp')
    prepositions: TextDist = lang.item_property('prepositions')
    nouns: TextDist = lang.item_property('nouns')
    verbs: TextDist = lang.item_property('verbs')
    articles: TextDist = lang.item_property('articles')
    adjectives: TextDist = lang.item_property('adjectives')
    adverbs: TextDist = lang.item_property('adverbs')
    auxiliaries: TextDist = lang.item_property('auxillaries')
    terminators: TextDist = lang.item_property('terminators')
    order_priorities: TextDist = lang.item_property('o_oprio')
    ship_instructions: TextDist = lang.item_property('instruct')
    ship_modes: TextDist = lang.item_property('smode')
    return_flags: TextDist = lang.item_property('rflag')
    part_containers: TextDist = lang.item_property('p_cntr')
    part_colors: TextDist = lang.item_property('colors')
    part_types: TextDist = lang.item_property('p_types')
    market_segments: TextDist = lang.item_property('msegmnt')
    nations: TextDist = lang.item_property('nations')
    regions: TextDist = lang.item_property('regions')


class PyTextPoolGen:

    def __init__(
            self,
            size: int,
            max_sentence_length: int,
            dists: TextDists,
    ) -> None:
        super().__init__()

        self._dists = check.not_none(dists)
        self._buf = bytearray(size + max_sentence_length)
        self._pos = 0
        self._last = None
        self._gen = IntGen(933588178, 0x7FFFFFFF)

        while self._pos < size:
            self._generate_sentence()

        del self._buf[size:]

    @property
    def buf(self) -> bytearray:
        return self._buf

    def _write(self, b: bytes) -> None:
        if not b:
            return
        bl = len(b)
        self._buf[self._pos:self._pos + bl] = b
        self._pos += bl
        self._last = b[-1]

    def _erase(self, i: int) -> None:
        if i > self._pos:
            raise ValueError(i)
        self._pos -= i
        if self._pos:
            self._last = self._buf[self._pos - 1]
        else:
            self._last = None

    def _rand(self, dist: TextDist) -> bytes:
        return dist.random_bytes_value(self._gen)

    def _generate_sentence(self) -> None:
        syntax = self._rand(self._dists.grammars)
        for i in range(0, len(syntax), 2):
            if syntax[i] == 86:  # 'V'
                self._generate_verb_phrase()
            elif syntax[i] == 78:  # 'N'
                self._generate_noun_phrase()
            elif syntax[i] == 80:  # 'P'
                preposition = self._rand(self._dists.prepositions)
                self._write(preposition)
                self._write(b' the ')
                self._generate_noun_phrase()
            elif syntax[i] == 84:  # 'T'
                self._erase(1)
                terminator = self._rand(self._dists.terminators)
                self._write(terminator)
            else:
                raise ValueError(f'Unknown token "{syntax[i]}"')
            if self._last != 32:  # ' '
                self._write(b' ')

    def _generate_verb_phrase(self) -> None:
        syntax = self._rand(self._dists.verb_phrase)
        for i in range(0, len(syntax), 2):
            if syntax[i] == 68:  # 'D'
                source = self._dists.adverbs
            elif syntax[i] == 86:  # 'V'
                source = self._dists.verbs
            elif syntax[i] == 88:  # 'X'
                source = self._dists.auxiliaries
            else:
                raise ValueError(f'Unknown token "{syntax[i]}"')
            word = self._rand(source)
            self._write(word)
            self._write(b' ')

    def _generate_noun_phrase(self) -> None:
        syntax = self._rand(self._dists.noun_phrase)
        for i in range(0, len(syntax)):
            if syntax[i] == 65:  # 'A'
                source = self._dists.articles
            elif syntax[i] == 74:  # 'J'
                source = self._dists.adjectives
            elif syntax[i] == 68:  # 'D'
                source = self._dists.adverbs
            elif syntax[i] == 78:  # 'N'
                source = self._dists.nouns
            elif syntax[i] == 44:  # ','
                self._erase(1)
                self._write(b', ')
                continue
            elif syntax[i] == 32:  # ' '
                continue
            else:
                raise ValueError(f'Unknown token "{syntax[i]}"')
            word = self._rand(source)
            self._write(word)
            self._write(b' ')


def py_gen_text_pool(size: int, max_sentence_length: int, dists: TextDists) -> bytearray:
    return PyTextPoolGen(size, max_sentence_length, dists).buf


# from . import _tpch  # noqa


_CY_ENABLED = True

try:
    if not _CY_ENABLED:
        raise ImportError

    from .._ext.cy.tpch import gen_text_pool as _cy_gen_text_pool
    from .._ext.cy.tpch import TextDist as CyTextDist
    from .._ext.cy.tpch import TextDists as CyTextDists

    def cy_gen_text_pool(size: int, max_sentence_length: int, dists: TextDists) -> bytearray:
        cy_dists = CyTextDists()
        for attr in dir(cy_dists):
            if not attr.startswith('_'):
                setattr(cy_dists, attr, CyTextDist(getattr(dists, attr).bytes_seq))
        return _cy_gen_text_pool(size, max_sentence_length, cy_dists)

    gen_text_pool = cy_gen_text_pool

except ImportError:
    gen_text_pool = py_gen_text_pool


class TextPool:

    DEFAULT_SIZE = 300 * 1024 * 1024
    MAX_SENTENCE_LENGTH = 256

    def __init__(self, size: int, dists: TextDists) -> None:
        check.not_none(dists)

        self._buf = gen_text_pool(size, self.MAX_SENTENCE_LENGTH, dists)

    @cached.function
    @classmethod
    def default(cls) -> 'TextPool':
        return cls(cls.DEFAULT_SIZE, TextDists.default())

    @property
    def size(self) -> int:
        return len(self._buf)

    def get_text(self, begin: int, end: int) -> str:
        check.arg(end <= len(self._buf))
        return self._buf[begin:end].decode('utf-8')


class RandomText(GenRandom):

    _LOW_LENGTH_MULTIPLIER = 0.4
    _HIGH_LENGTH_MULTIPLIER = 1.6

    def __init__(self, seed: int, pool: TextPool, average_text_length: float, expected_row_count: int = 1) -> None:
        super().__init__(IntGen(seed, expected_row_count * 2))

        self._pool = pool
        self._min_length = int(average_text_length * self._LOW_LENGTH_MULTIPLIER)
        self._max_length = int(average_text_length * self._HIGH_LENGTH_MULTIPLIER)

    def next_value(self) -> str:
        offset = self._gen.rand(0, self._pool.size - self._max_length)
        length = self._gen.rand(self._min_length, self._max_length)
        return self._pool.get_text(offset, offset + length)


if __name__ == '__main__':
    TextPool.default()  # noqa
