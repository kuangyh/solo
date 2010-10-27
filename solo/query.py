# -*- coding: utf-8 -*-
import pipe
import util

class QueryRunner(object):
    def __init__(self, query, compiled, codesrc):
        self.query = query
        self.__compiled = compiled 
        self.codesrc = codesrc

    def __call__(self, src, ctx = None):
        if ctx is None:
            return self.__compiled(src)
        else:
            with ctx:
                return self.__compiled(src)

    def __lshift__(self, src):
        try:
            self(src)
            return True
        except BaseException, e:
            return False

    def __invert__(self):
        return self.query

class Query(object):
    def __init__(self, procs = ()):
        self.procs = procs

    def __getattr__(self, name):
        return self + AttrMacro(name)
        
    def __getitem__(self, item):
        return self + ItemMacro(item)

    def __call__(self, *args, **kwargs):
        return self + CallMacro(args, kwargs)

    def __add__(self, other):
        """
        Combine two queries or other processor(s)
        """
        if len(self.procs) == 0:
            if isinstance(other, Query):
                return other
            elif isinstance(other, QueryRunner):
                return ~other
            elif isinstance(other, Macro) or callable(other):
                return type(self)((other,))
            else:
                return type(self)((DataMacro(other),))
        else:
            if isinstance(other, Query):
                return type(self)(self.procs + (~other,))
            elif isinstance(other, Macro) or callable(other):
                return type(self)(self.procs + (other,))
            else:
                return type(self)(self.procs + ~(type(self)((DataMacro(other),))))

    def __compile(self):
        # Special cases, return shortcut callable
        if len(self.procs) == 0:
            return pipe.PIPE, ''
        if len(self.procs) == 1 and not isinstance(self.procs[0], Macro):
            return self.procs[0], ''

        base, params = '_', ()
        for node in self.procs:
            if isinstance(node, Macro):
                base, params = node.gencode(base, params)
            else:
                base = 'p%d(%s)' % (len(params), base)
                params = params + (node,)
        # prepare namespace
        ns = {}
        for idx in xrange(len(params)):
            ns['p%d' % (idx,)] = params[idx]

        codesrc = 'lambda _:' + base
        return eval(codesrc, ns), base

    def __invert__(self):
        return QueryRunner(self, *self.__compile())

class Macro(object):
    @staticmethod
    def _compile_value(value, params):
        if value is None or type(value) in (int, float, str, unicode, bool):
            return repr(value), params, False
        elif isinstance(value, Query):
            return 'p%d(_)' % (len(params),), params + (~value,), True
        elif type(value) in (tuple, list):
            orig_params = params
            has_query = False
            codes = []
            for item in value:
                code, params, tmp = Macro._compile_value(item, params)
                codes.append(code)
                has_query = has_query or tmp
            if has_query:
                if type(value) == tuple:
                    t = '(%s,)'
                else:
                    t = '[%s]'
                return t % (','.join(codes),), params, True
            else:
                return 'p%d' % (len(orig_params),), orig_params + (value,), False
        elif type(value) == dict:
            orig_params = params
            has_query = False
            codes = []
            for k, v in value.iteritems():
                k_code, params, tmp1 = Macro._compile_value(k, params)
                v_code, params, tmp2 = Macro._compile_value(v, params)
                codes.append('%s:%s' % (k_code, v_code))
                has_query = has_query or tmp1 or tmp2
            if has_query:
                return '{%s}' % (','.join(codes),), params, True
            else:
                return 'p%d' % (len(orig_params),), orig_params + (value,), False
        else:
            return 'p%d' % (len(params),), params + (value,), False

    @staticmethod
    def compile_value(value, params):
        return Macro._compile_value(value, params)[:2]

class DataMacro(Macro):
    def __init__(self, value):
        self.value = value

    def gencode(self, base, params):
        return Macro.compile_value(self.value, params)

class AttrMacro(Macro):
    def __init__(self, name):
        self.name = name

    def gencode(self, base, params):
        return '%s.%s' % (base, self.name,), params

class ItemMacro(Macro):
    def __init__(self, key):
        self.key = key

    def gencode(self, base, params):
        keycode, params = Macro.compile_value(self.key, params)
        return '%s[%s]' % (base, keycode,), params

class CallMacro(Macro):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def gencode(self, base, params):
        args_code, params = Macro.compile_value(self.args, params)
        kwargs_code, params = Macro.compile_value(self.kwargs, params)
        return '%s(*%s, **%s)' % (base, args_code, kwargs_code), params

Q = Query()

if __name__ == '__main__':
    v = ~(Q + [1,2,[4,[6,5]],3,[4,Q]])
    print v.codesrc
    print v({'delim' : ':', 'value' : 'Pudding'})
