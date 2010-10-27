# -*- coding: utf-8 -*-

"""
Iterator based batch handling
"""

import itertools
import query
import pattern

class MethodSwitch(object):
    ROUTE	= ()
    
    def __init__(self, *args, **kwargs):
        self.__init_args = args
        self.__init_kwargs = kwargs

    def perform(self, src):
        raise NotImplementedError

    def __call__(self, src):
        for name in self.ROUTE:
            if hasattr(src, name):
                return getattr(src, name)(*self.__init_args, **self.__init_kwargs)
        return self.perform(src)

class Map(MethodSwitch):
    ROUTE	= ('map',)
    def __init__(self, op):
        op = query.Q + op
        MethodSwitch.__init__(self, op)
        self.op = op
        self.op_call = ~self.op

    def perform(self, value):
        return map(self.op_call, pattern.makeiter(value))

class Filter(MethodSwitch):
    ROUTE	= ('filter',)    
    def __init__(self, op):
        op = pattern.makepat(op)
        MethodSwitch.__init__(self, op)
        self.op = op        
        self.op_call = ~self.op

    def perform(self, value):
        def dotest(value):
            try:
                self.op_call(value)
                return True
            except BaseException, e:
                return False
        return filter(dotest, pattern.makeiter(value))

