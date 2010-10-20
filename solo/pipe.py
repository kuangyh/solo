# -*- coding: utf-8 -*-

class Pipe(tuple):
    """
    Function combinator
    """
    def __add__(self, other):
        """
        Combine to pipes or combine pipe and raw function
        """
        if type(other) == type(self):
            return self.__class__(tuple.__add__(self, other))
        else:
            return self.__class__(tuple.__add__(self, (other,)))
    __rshift__ = __add__

    def __call__(self, value):
        for func in self:
            value = func(value)
        return value

    @classmethod
    def operator(cls, name, factory):
        """
        Register a operator on the class, which support pipe chaining
        """
        def chain_factory(self, *args, **kwargs):
            return self + factory(*args, **kwargs)
        chain_factory.__name__ = name
        setattr(cls, name, chain_factory)

def pipe(*funcs):
    """
    Covinient function to create pipe, pipe(a, b, c) etc.
    """
    return Pipe(funcs)

class Try(tuple):
    """
    Try each function, until one of it properbily return
    """
    def __add__(self, other):
        if type(other) == type(self):
            return self.__class__(tuple.__add__(self, other))
        else:
            return self.__class__(tuple.__add__(self, (other,)))

    def __call__(self, value):
        last_error = None
        for func in self:
            try:
                return func(value)
            except BaseException, e:
                last_error = e
        if last_error is not None:
            raise last_error
        return None
    
def tryall(*funcs):
    return Try(funcs)

