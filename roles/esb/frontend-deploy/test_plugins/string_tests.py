#!/usr/bin/python
# -*- conding: utf-8 -*-

import re

def invert_match(pattern, value):
    _re = re.compile(pattern);
    _bool = __builtins__.get('bool')
    return _bool(getattr(_re, 'search', 'search')(value))

class TestModule(object):
    def tests(self):
        return {
            'invert_match': invert_match,
        }
