# -*- coding: utf-8 -*-

"""
Scala-like pattern matching with object-oriented support (extract from complex objects)
"""

import context
import pipe

class NotMatchException(Exception): pass

class Pattern(pipe.Pipe):
    def orelse(self, other):
        return Pattern((context.tryall(self, other),))
    __or__ = orelse

    def default(self, value):
        return self.orelse(Default(value))

    def test(self, value):
        try:
            self(value)
            return True
        except BaseException, e:
            return False

class Default(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, any):
        return self.value

######################################
# Binding a value to current context
######################################

class Bind(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, value):
        context.curr()[self.name] = value
        return value
Pattern.operator('bind', Bind)
Pattern.operator('__mod__', Bind)

##########################
# Checking single value
##########################

class Equal(object):
    def __init__(self, *options):
        self.options = options

    def __call__(self, value):
        if value not in self.options:
            raise NotMatchException(self, value)
        return value
Pattern.operator('equal', Equal)

class Type(object):
    def __init__(self, *types):
        self.types = types

    def __call__(self, value):
        if not isinstance(value, self.types):
            raise NotMatchException(self, value)
        return value
Pattern.operator('type', Type)

class Check(object):
    def __init__(self, *funcs):
        self.funcs = funcs

    def __call__(self, value):
        for func in self.funcs:
            if not func(value):
                raise NotMatchException(self, value)
        return value
Pattern.operator('check', Check)

class Guard(object):
    def __init__(self, *funcs):
        self.func = funcs

    def __call__(self, value):
        ctx = context.curr()
        for func in self.funcs:
            if not func(ctx):
                raise NotMatchException(self, value)
        return value
    
############################
# Extracting data structure
############################
class Seq(object):
    def __init__(self, *elements):
        self.elements = elements

    def __call__(self, value):
        it = iter(value)
        for elpat in self.elements:
            elpat(it.next())
        return it
Pattern.operator('seq', Seq)

class Nil(object):
    def __call__(self, value):
        try:
            value.next()
            raise NotMatchException(self, value)
        except StopIteration, e:
            return value
NIL = Nil()

def compile_match(src):
    """
    compile a data pattern into matching operators
    """
    if isinstance(src, type):
        return Type(src)
    elif callable(src):
        return Check(src)
    elif isinstance(src, (list, tuple)):
        compiled = map(compile_match, src)
        found = False
        for item in compiled:
            if not isinstance(item, Equal):
                found = True
                break
        if found:
            return Seq(*compiled)
        else:
            return Equal(src)
    else:
        return Equal(src)
Pattern.operator('match', compile_match)
Pattern.operator('__or__', compile_match)

#########################################
# Extractors, extracting other objects
# Make it a sequence for futher matching
#########################################
class MappingExtractor(object):
    def __init__(self, *keys, **defaults):
        self.keys = keys
        self.defaults = defaults

    def __call__(self, value):
        output = []
        for key in self.keys:
            try:
                v = value[key]
            except KeyError, e:
                v = self.defaults[key]
            output.append(v)
        return tuple(output)
Pattern.operator('items', MappingExtractor)
Pattern.operator('i', MappingExtractor)
Pattern.operator('select', MappingExtractor)

class ObjectExtractor(object):
    def __init__(self, *keys, **defaults):
        self.keys = keys
        self.defaults = defaults

    def __call__(self, value):
        output = []
        for key in self.keys:
            try:
                v = getattr(value, key)
            except AttributeError, e:
                v = self.defaults[key]
            output.append(v)
        return tuple(output)
Pattern.operator('attrs', ObjectExtractor)
Pattern.operator('a', ObjectExtractor)

import re
class RegexExtractor(object):
    def __init__(self, pat):
        self.regex = re.compile(pat)

    def __call__(self, value):
        m = self.regex.match(value)
        if m is None:
            raise NotMatchException(self, value)
        ctx = context.curr()
        if ctx is not None:
            for key, value in m.groupdict().iteritems():
                ctx[key] = value
        return m.groups()
Pattern.operator('re', RegexExtractor)

def compile_extractor(src):
    if isinstance(src, type) and hasattr(src, '__extractor__'):
        return Pattern((Type(src), src.__extractor__)) # check type, then use default extractor
    elif callable(src):
        return src              # invoke that function
    elif isinstance(src, basestring):
        return RegexExtractor(src) # regex matching and extracting
    elif isinstance(src, (list, tuple)):
        return MappingExtractor(*src)
    else:
        # Perform a normal match
        return compile_match(src)
Pattern.operator('__getitem__', compile_extractor)

