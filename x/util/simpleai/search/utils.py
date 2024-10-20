import collections
import heapq
import random


class LifoList(collections.deque):
    """List that pops from the end."""

    def sorted(self):
        return list(self)[::-1]


class FifoList(collections.deque):
    """List that pops from the beginning."""

    def pop(self):
        return super(FifoList, self).popleft()

    def sorted(self):
        return list(self)


class BoundedPriorityQueue:
    def __init__(self, limit=None, *args):
        self.limit = limit
        self.queue = list()

    def __getitem__(self, val):
        return self.queue[val]

    def __len__(self):
        return len(self.queue)

    def append(self, x):
        heapq.heappush(self.queue, x)
        if self.limit and len(self.queue) > self.limit:
            self.queue.remove(heapq.nlargest(1, self.queue)[0])
            heapq.heapify(self.queue)

    def pop(self):
        return heapq.heappop(self.queue)

    def extend(self, iterable):
        for x in iterable:
            self.append(x)

    def clear(self):
        self.queue.clear()

    def remove(self, x):
        self.queue.remove(x)
        heapq.heapify(self.queue)

    def sorted(self):
        return heapq.nsmallest(len(self.queue), self.queue)


class InverseTransformSampler:
    def __init__(self, weights, objects):
        assert weights and objects and len(weights) == len(objects)
        self.objects = objects
        tot = float(sum(weights))
        if tot == 0:
            tot = len(weights)
            weights = [1 for x in weights]
        accumulated = 0
        self.probs = []
        for w, x in zip(weights, objects):
            p = w / tot
            accumulated += p
            self.probs.append(accumulated)

    def sample(self):
        target = random.random()
        i = 0
        while i + 1 != len(self.probs) and target > self.probs[i]:
            i += 1
        return self.objects[i]


def _generic_arg(iterable, function, better_function):
    values = [function(x) for x in iterable]
    better_value = better_function(values)
    candidates = [x for x, value in zip(iterable, values) if value == better_value]
    return random.choice(candidates)


def argmin(iterable, function):
    return _generic_arg(iterable, function, min)


def argmax(iterable, function):
    return _generic_arg(iterable, function, max)
