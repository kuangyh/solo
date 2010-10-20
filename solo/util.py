# -*- coding: utf-8 -*-

"""
Useful tricks
"""

import types

class ContextFunction(object):
    """
    Wrap a function, make it collect arguments from a mapping instead of argument list

    func = ContextFunction(lambda x, y = 10: x + y)
    func({'x' : 20}) => 30
    func({'x' : 20, 'y' : 22}) => 42
    """
    def __init__(self, orig):
        self.orig = orig
        func = orig
        if not hasattr(func, '__code__'):
            func = func.__call__
        if isinstance(func, types.MethodType):
            func = func.im_func
            func_args = func.__code__.co_varnames[1 : func.__code__.co_argcount]
        else:
            func_args = func.__code__.co_varnames[:func.__code__.co_argcount]

        num_defaults = len(func.func_defaults or ())
        if num_defaults > 0:
            self.required_args = func_args[:-num_defaults]
            self.optional_args = func_args[-num_defaults:]
        else:
            self.required_args = func_args
            self.optional_args = ()

    def __call__(self, ctx):
        args = map(ctx.__getitem__, self.required_args)
        kwargs = {}
        for name in self.optional_args:
            if name in ctx:
                kwargs[name] = ctx[name]
        return self.orig(*args, **kwargs)

ctxfun = ContextFunction

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

class Invoke(object):
    """
    Operation chain on a undefined object

    op = ~I[0].upper()
    op(['abc', 'def']) => 'ABC'
    """
    
    def __init__(self, codesrc = '_', paramlist = ()):
        self.__codesrc = codesrc
        self.__paramlist = paramlist
        self.__invoker = eval('lambda _,p:' + codesrc)

    def invoker_invoke(self, obj):
        return self.__invoker(obj, self.__paramlist)

    def __invert__(self):
        """
        Provide the object, invoke it
        """
        return self.invoker_invoke

    def __getattr__(self, attrname):
        return type(self)('%s.%s' % (self.__codesrc, attrname), self.__paramlist)

    def __getitem__(self, name):
        idx = len(self.__paramlist)
        return type(self)(self.__codesrc + '[p[%d]]' % (idx,), self.__paramlist + (name,))

    def __call__(self, *args, **kwargs):
        idx = len(self.__paramlist)
        return type(self)(self.__codesrc + '(*p[%d],**p[%d])' % (idx, idx + 1),
                          self.__paramlist + (args, kwargs))

IN = Invoke('_', ())
import context
IC = Invoke('p[0]()', (context.curr,))

