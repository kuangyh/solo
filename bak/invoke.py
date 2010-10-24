# -*- coding: utf-8 -*-

"""
Somewhat hard to explain
"""
import ctx
import tpl

class Invoke(object):
    def __asop(src):
        if isinstance(src, Invoke):
            return ~src
        raise TypeError, src
    __conf_ctx = ctx.Context({'conf/asop' : __asop})
    
    def __init__(self, codesrc, params):
        self.__codesrc = codesrc
        self.__params = params
        self.__func = eval('lambda _,p:' + codesrc)

    def __invoke(self, datasrc):
        return self.__func(datasrc, self.__params)

    def __invert__(self):
        return self.__invoke

    @staticmethod
    def _compile_param(idx, param):

        # For simple data type, directly exit it
        if type(param) in (int, float, basestring, bool):
            return repr(param), ()

        with Invoke.__conf_ctx:
            t = tpl.TPL(param)
        if isinstance(t, tpl.ConstTemplate):
            return 'p[%d]' % (idx,), (param,)
        else:
            return '(p[%d](_))' % (idx,), (t,)

    def __extend(self, codesrc, params = ()):
        return type(self)(self.__codesrc + codesrc, self.__params + params)

    def __getattr__(self, attrname):
        return self.__extend('.' + attrname)

    def __getitem__(self, key):
        selector, data = Invoke._compile_param(len(self.__params), key)
        return self.__extend('[%s]' % (selector,), data)

    def __call__(self, *args, **kwargs):
        idx = len(self.__params)
        args_sel, args_data = Invoke._compile_param(idx, list(args))
        kwargs_sel, kwargs_data = Invoke._compile_param(idx + 1, kwargs)
        return self.__extend('(*%s,**%s)' % (args_sel, kwargs_sel),
                             args_data + kwargs_data)

IN = Invoke('_', ())
IG = Invoke('globals()', ())
IC = Invoke('p[0]()', (ctx.curr,))

def I(start):
    return Invoke('p[0]', (start,))

