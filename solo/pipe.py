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

    def __call__(self, value):
        for func in self:
            value = func(value)
        return value

PIPE = Pipe()

def combine(*funcs):
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

