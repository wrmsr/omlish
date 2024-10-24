#!/usr/bin/env python
import collections
import math

import numpy


class Counter(collections.defaultdict):
    """
    Counter of examples. Counts the total of examples added
    and also the times that the target of that example appears.

    To add an example use the `add` method and to check the
    values use it like a dictionary.
    """

    def __init__(self, target):
        super(Counter, self).__init__(int)
        self.target = target
        self.total = 0

    def add(self, example):
        value = self.target(example)
        self[value] += 1
        self.total += 1


class OnlineEntropy(Counter):
    def get_entropy(self):
        s = 0.0
        for count in list(self.values()):
            p = count / float(self.total)
            s += p * math.log2(p)
        return -s


class OnlineInformationGain:
    def __init__(self, attribute, target):
        self.attribute = attribute
        self.H = OnlineEntropy(target)
        self.G = collections.defaultdict(lambda: OnlineEntropy(target))

    def add(self, example):
        self.H.add(example)
        value = self.attribute(example)
        self.G[value].add(example)

    def get_target_class_counts(self):
        return self.H

    def get_branches(self):
        return list(self.G.items())

    def get_gain(self):
        H1 = self.H.get_entropy()
        H2 = 0.0
        for G in list(self.G.values()):
            w = G.total / float(self.H.total)
            H2 += w * G.get_entropy()
        return H1 - H2


class OnlineLogProbability:
    def __init__(self):
        self.d = collections.defaultdict(int)
        self._logtotal = None

    def add(self, x):
        if self._logtotal is not None:
            raise ValueError('OnlineLogProbability is frozen since first read')
        self.d[x] += 1

    def __getitem__(self, x):
        if x not in self:
            raise KeyError(x)
        if self._logtotal is None:
            self._logtotal = numpy.log(sum(self.d.values()))
        return numpy.log(self.d[x]) - self._logtotal

    def __contains__(self, x):
        return x in self.d

    def __iter__(self):
        return iter(self.d)

    def __len__(self):
        return len(self.d)

    def iteritems(self):
        for x in self.d:
            yield x, self[x]
