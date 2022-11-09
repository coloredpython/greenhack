import inspect
import typing
from functools import wraps

import greenlet


def exempt(fn=None):
    """
    A coroutine produced by `fn` is exempted from the current greenlet
    and will be executed in another greenlet (the one with an event loop).

    After decorating, a coroutine function `fn` is turned into a regular function.
    """

    def decorate(fn):
        assert inspect.iscoroutinefunction(fn) or type(fn).__module__ == 'builtins'

        @wraps(fn)
        def replace_fn(*args, **kwargs):
            current = greenlet.getcurrent()
            co = fn(*args, **kwargs)
            try:
                other = current.async_greenlet
            except AttributeError:
                # TODO check a context var, if set, do nothing, i. e. return co
                raise

            return other.switch(co)

        return replace_fn

    # This makes the decorator usable as both @exempt and @exempt()
    return decorate(fn) if fn else decorate

