# -*- coding: utf-8 -*-

"""
Maintain a ``global'' dict stack

def doit():
    Context.curr()['a'] = 10
...

ctx = Context()
with ctx:
    doit()
ctx => { 'a' : 10 }

"""

import threading
import types

class Context(dict):
    __thstat__ = threading.local()
    __thstat__.curr = None

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__prev = None

    @classmethod
    def curr(cls):
        """
        Get current context in this thread of execution
        """
        return cls.__thstat__.curr

    @classmethod
    def switch(cls, ctx):
        """
        Switch context in this thread of execution, return the old current context
        """
        ret = cls.__thstat__.curr
        cls.__thstat__.curr = ctx
        return ret
    
    def __enter__(self):
        """
        In this thread of excution, use this context as current context
        """
        if self.__prev is not None:
            raise ValueError, 'Already in stack'
        self.__prev = Context.switch(self)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the scope of context, restore prev context
        """
        if self.__class__.curr() != self:
            raise ValueError, 'Invalid thread of execution'
        self.__class__.switch(self.__prev)
        self.__prev = None

curr = Context.curr
ctx = Context

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

