# -*- coding: utf-8 -*-

"""
Extract value(s) from object
"""

import re
import pattern

class Regex(object):
    def __init__(self, regex):
        self.regex = re.compile(regex)

    def __call__(self, value):
        m = self.regex.match(value)
        if m is None:
            raise pattern.NotMatchException(self, value)
        return (m.groups(), m.groupdict())

R = Regex

