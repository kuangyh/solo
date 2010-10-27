# -*- coding: utf-8 -*-

class Const(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, any):
        return self.value

def makeiter(src):
    """
    Only consier list and iterator (with __iter__ and next) iterable
    for other value, turn it to a iterator with only one item
    """
    if hasattr(src, '__iter__') and hasattr(src, 'next'):
        return src
    elif isinstance(src, list):
        return iter(src)
    else:
        return iter([src])
