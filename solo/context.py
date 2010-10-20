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

