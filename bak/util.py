# -*- coding: utf-8 -*-

"""
Useful tricks
"""

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

def maketest(orig):
    """
    Make a pattern or function to a test function (returns True or False)
    Catch it's exception and consider False instread of throw out
    """    
    # for pattern, use it's own test interface
    import pattern
    if isinstance(orig, pattern.Pattern):
        return orig.test

    # for other function, catch exception and turn it to False
    def func(value):
        try:
            return bool(orig(value))
        except BaseException, e:
            return False

