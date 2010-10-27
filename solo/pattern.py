# -*- coding: utf-8 -*-

"""
Pattern matching processors for query
"""

import query
import context

class NotMatchException(Exception): pass

############################
# Play with context
############################
class Bind(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, value):
        curr = context.curr()
        if curr is not None:
            curr[self.name] = value
        return value

###############################
# Matching single value
###############################
class Value(object):
    def __init__(self, *options):
        self.options = options

    def __call__(self, value):
        if value not in self.options:
            raise NotMatchException(self, value)
        return value

class Type(object):
    def __init__(self, checktype):
        self.checktype = checktype

    def __call__(self, value):
        if not isinstance(value, self.checktype):
            raise NotMatchException(self, value)
        return value

class Test(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, value):
        try:
            ret = self.func(value)
        except BaseException, e:
            ret = False
        if not ret:
            raise NotMatchException(self, value)
        return value

class All(object):
    def __init__(self, *checks):
        self.checks = map(query.Q.__add__, checks)
        self.checks_call = map(lambda x: ~x, self.checks)

    def __call__(self, value):
        for check in self.checks_call:
            # TODO: more strict checking
            if not check(value):
                raise NotMatchException(self, value)
        return value

class Choice(object):
    def __init__(self, *checks):
        self.checks = map(query.Q.__add__, checks)
        self.checks_call = map(lambda x: ~x, self.checks)

    def __call__(self, value):
        last_error = None
        for check in self.checks_call:
            try:
                return check(value)
            except BaseException, e:
                last_error = e
        if last_error is not None:
            raise last_error
        else:
            return value

##############################
# Match data-struct
##############################
class SeqMatch(object):
    def __init__(self, match, rest):
        self.match = match
        self.rest = rest

    def __iter__(self):
        return self.rest
    
        
class Seq(object):
    def __init__(self, matches):
        # Make all Query
        self.matches = matches
        self.matches_invoke = map(lambda x: ~x, self.matches)

    def __call__(self, src):
        it = iter(src)
        output = []
        for match in self.matches_invoke:
            output.append(match(it.next()))
        return SeqMatch(output, it)

class Mapping(object):
    def __init__(self, matches):
        self.matches = matches
        self.matches_invoke = map(lambda x: (x[0], ~x[1]), matches.iteritems())

    def __call__(self, src):
        output = {}
        for key, invoke in self.matches_invoke:
            output[key] = invoke(src[key])
        return output

def match(pattern):
    if isinstance(pattern, query.Query):
        return Test(~pattern)
    elif isinstance(pattern, type):
        return Type(pattern)
    elif callable(pattern):
        return Test(pattern)
    elif isinstance(pattern, (list, tuple)):
        has_test = False
        output = []
        for item in pattern:
            compiled = match(item)
            output.append(compiled)
            has_test = has_test or (not isinstance(compiled, Value))
        if has_test:
            output = map(query.Q.__add__, output)
            return Seq(output)
        else:
            return Value(pattern)
    elif isinstance(pattern, dict):
        has_test = False
        output = []
        for k, v in pattern.iteritems():
            compiled = match(v)
            output.append((k, compiled))
            has_test = has_test or (not isinstance(compiled, Value))
        if has_test:
            output = dict(map(lambda x: (x[0], query.Q + x[1]), output))
            return Mapping(output)
        else:
            return Value(pattern)
    else:
        return Value(pattern)

def makepat(value):
    if isinstance(value, query.Query):
        return value
    else:
        return query.Q + match(value)

if __name__ == '__main__':
    Q = query.Q

    q = ~(Q['delim'].join(Q['data']))
    print q({'delim' : ':', 'data' : ['a','b','c']})
