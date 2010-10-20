# -*- coding: utf-8 -*-

"""
Batch, Relational data processing
"""
import pipe
import pattern
import util
import itertools

class Hook(object):
    METHOD	= None
    
    def __init__(self, *args, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs

    def perform(self, value):
        raise NotImplementedError

    def __call__(self, obj):
        if hasattr(obj, self.METHOD):
            return getattr(obj, self.METHOD)(*self._init_args, **self._init_kwargs)
        else:
            return self.perform(obj)

class DSet(pipe.Pipe): pass

class Map(Hook):
    METHOD = 'map'
    def __init__(self, func):
        Hook.__init__(self, func)
        self.func = func

    def perform(self, value):
        it = util.makeiter(value)
        return itertools.imap(self.func, it)
DSet.operator('map', Map)

class Filter(Hook):
    METHOD = 'filter'
    def __init__(self, func):
        Hook.__init__(self, func)

        self.test = func
        self.filter_func = util.maketest(func)

    def perform(self, value):
        it = util.makeiter(value)
        return itertools.ifilter(self.filter_func, it)
DSet.operator('filter', Filter)

class Limit(Hook):
    METHOD = 'limit'
    def __init__(self, *args):
        Hook.__init__(self, *args)
        if isinstance(args[0], slice):
            tmp = args[0]
        else:
            tmp = slice(*args)
        self.start, self.stop, self.step = tmp.start, tmp.stop, tmp.step

    def perform(self, value):
        it = util.makeiter(value)
        return itertools.islice(it, self.start, self.stop, self.step)
DSet.operator('limit', Limit)


def _makeselect(*keys, **defaults):
    if len(keys) == 1 and callable(keys[0]):
        return keys[0]
    else:
        return pattern.MappingExtractor(*keys, **defaults)

class Order(Hook):
    METHOD = 'order'
    def __init__(self, *keys, **defaults):
        Hook.__init__(self, *keys, **defaults)
        self.keyfunc = _makeselect(*keys, **defaults)
        self.is_reverse = defaults.get('reverse', False)

    def perform(self, value):
        value = list(value)
        value.sort(key = self.keyfunc, reverse = self.is_reverse)
        return value
DSet.operator('order', Order)

class GroupBy(Hook):
    METHOD = 'groupby'
    def __init__(self, *keys, **defaults):
        Hook.__init__(self, *keys, **defaults)
        self.keyfunc = _makeselect(*keys, **defaults)

    def perform(self, value):
        it = util.makeiter(value)
        output = {}
        for item in it:
            key = self.keyfunc(item)
            output.setdefault(key, []).append(item)
        return output.iteritems()
DSet.operator('groupby', GroupBy)

class Join(Hook):
    METHOD = 'join'
    def __init__(self, other):
        Hook.__init__(self, other)
        self.other = list(other)

    def perform(self, value):
        it = util.makeiter(value)
        for x in it:
            for y in self.other:
                yield (x, y)
DSet.operator('join', Join)


import lxml
import lxml.etree

class XPath(Hook):
    METHOD = 'xpath'
    def __init__(self, path):
        Hook.__init__(self, path)
        self.path = path

    def perform(self, nodelist):
        # Because of the hook, it must be the nodelist, not a single
        # node (which will trigger node.xpath)
        output = []
        for node in nodelist:
            output.extend(node.xpath(self.path))
        return output
DSet.operator('xml', XPath)
