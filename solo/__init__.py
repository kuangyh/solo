# -*- coding: utf-8 -*-

import query
from query import Q

import pattern
from pattern import NIL
import dset
import extract
import context

makectx = context.ctx
currctx = context.curr

from util import Const, Var


class Magic(object):
    """
    Give query more magics
    """
    def __getattr__(self, name):
        return Var(name)

    def __getitem__(self, value):
        return Q + Const(value)

    def __call__(self, func, *args, **kwargs):
        return lambda value: func(value, *args, **kwargs)
    
I = Magic()

query.Query.__div__ = lambda self, pat: self + pattern.match(pat)
query.Query.__and__ = lambda self, pats: self + pattern.All(*pats)
query.Query.__or__ = lambda self, pats: self + pattern.Choice(*pats)

query.Query.__floordiv__ = lambda self, pat: self + dset.Filter(pat)
query.Query.__rshift__ = lambda self, pat: self + dset.Map(pat)
