from __future__ import unicode_literals

import json

from py_mini_racer import py_mini_racer
from six import text_type

from .base import JavaScriptError


class JavaScriptRunner(object):

    def __init__(self):
        self.ctx = py_mini_racer.MiniRacer()

    def __setitem__(self, key, value):
        json_value = json.dumps(value, separators=(',', ':'))
        self.ctx.eval('var {} = {}'.format(key, json_value))

    def evaluate(self, script):
        try:
            script = script.read()
        except AttributeError:
            pass
        try:
            result = self.ctx.eval(script)
        except py_mini_racer.MiniRacerBaseException as e:
            errmsg = text_type(e)
            errmsg = errmsg[(errmsg.find('\n') + 1):]
            raise JavaScriptError(errmsg)
        return result
