import importlib

from .base import JavaScriptError

__all__ = ['JavaScriptError', 'JavaScriptRunner']


candidates = [
    ('javascriptcore', 'WebKit'),
    ('miniracer', 'py_mini_racer'),
]

for candidate, dependency in candidates:
    try:
        importlib.import_module(dependency)
    except ImportError as e:
        continue
    module = importlib.import_module('.{}'.format(candidate), package=__name__)
    JavaScriptRunner = module.JavaScriptRunner
    break
else:
    raise JavaScriptError('No suitable runtime. Tried: {}'.format(
        ', '.join('{0} (failed to import {1})'.format(*c) for c in candidates),
    ))
