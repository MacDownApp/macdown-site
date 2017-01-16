import WebKit

from .base import JavaScriptError


class JavaScriptRunner(object):

    def __init__(self):
        self.ctx = WebKit.JSContext.alloc().init()

    def __setitem__(self, key, value):
        self.ctx.setObject_forKeyedSubscript_(value, key)

    def evaluate(self, script):
        try:
            script = script.read()
        except AttributeError:
            pass
        result = self.ctx.evaluateScript_(script)
        exception = self.ctx.exception()
        if exception:
            raise JavaScriptError(exception)
        return result
