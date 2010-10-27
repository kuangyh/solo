# -*- coding: utf-8 -*-

"""
Extract value(s) from object
"""

import re
import pattern
import context

class Regex(object):
    def __init__(self, regex):
        self.regex = re.compile(regex)

    def __call__(self, value):
        m = self.regex.match(value)
        if m is None:
            raise pattern.NotMatchException(self, value)
        c = context.curr()
        if c is not None:
            for key, value in m.groupdict().iteritems():
                c[key] = value
        return m.groups()

R = Regex

