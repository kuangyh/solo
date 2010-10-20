# -*- coding: utf-8 -*-

"""
A Tempalte system to convert data
Nothing to do with HTML etc.
Think about XLST that transform RSS to ATOM
"""
import util
import context

class _Template(object):
    @staticmethod
    def asop(src):
        if callable(src):
            return src
        raise TypeError, src

    @staticmethod
    def compile(src):
        ctx = context.curr()
        if ctx is not None:
            asop = ctx.get('conf/asop', _Template.asop)
        else:
            asop = _Template.asop
        try:
            return asop(src)
        except BaseException, e:
            pass        
        if isinstance(src, (list, dict)):
            return CollTemplate(src)
        else:
            return ConstTemplate(src)
Template = _Template.compile

class ConstTemplate(_Template):
    def __init__(self, src):
        self.value = src

    def __call__(self, datasrc):
        return self.value

class _CollTemplate(_Template):
    def __init__(self,  tpl, ops):
        self.tpl = tpl
        self.ops = ops

    def __call__(self, datasrc):
        output = type(self.tpl)(self.tpl) # quick shallow copy for dict and list
        for key, op in self.ops:
            output[key] = op(datasrc)
        return output

    @staticmethod
    def compile(src):
        output_type = type(src)
        ops = []
        idx = 0
        if isinstance(src, list):
            tpl = []
            for value in src:
                op = Template(value)
                if isinstance(op, ConstTemplate):
                    tpl.append(value)
                else:
                    tpl.append(None)
                    ops.append((idx, op))
                idx += 1
        else:
            tpl = {}
            for key, value in src.iteritems():
                op = Template(value)
                if isinstance(op, ConstTemplate):
                    tpl[key] = value
                else:
                    ops.append((key, op))
        if len(ops) == 0:
            return ConstTemplate(src)
        else:
            return _CollTemplate(tpl, ops)
CollTemplate = _CollTemplate.compile

#Operators
class WithTemplate(_Template):
    def __init__(self, withpat, do):
        self.withpat = Template(withpat)
        self.do = Template(do)

    def __call__(self, src):
        return self.do(self.withpat(src))

class IterTemplate(_Template):
    def __init__(self, withpat, do):
        self.withpat = Template(withpat)
        self.do = Template(do)

    def __call__(self, src):
        it = util.makeiter(self.withpat(src))
        return map(self.do, it)        

class CaseTemplate(_Template):
    def __init__(self, *cases):
        self.cases = []
        for idx in range(0, len(cases), 2):
            self.cases.append((util.maketest(Template(cases[idx])), Template(cases[idx + 1])))
            
    def __call__(self, src):
        import pattern
        for test, tpl in self.cases:
            if test(src):
                return tpl(src)
        raise pattern.NotMatchException(self, src)

class MatchTemplate(_Template):
    def __init__(self, *cases):
        self.cases = []
        for idx in range(0, len(cases), 2):
            self.cases.append((Template(cases[idx]), Template(cases[idx + 1])))
            
    def __call__(self, src):
        import pattern
        for pat, tpl in self.cases:
            try:
                ex = pat(src)
            except BaseException, e:
                continue
            return tpl(ex)        
        raise pattern.NotMatchException(self, src)
    
WITH = WithTemplate
FOR = IterTemplate
CASE = CaseTemplate
MATCH = MatchTemplate
CONST = ConstTemplate
TPL = Template

