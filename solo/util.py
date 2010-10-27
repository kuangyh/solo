# -*- coding: utf-8 -*-

class Const(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, any):
        return self.value

