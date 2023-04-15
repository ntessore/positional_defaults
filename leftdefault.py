# license: MIT
'''Support for default arguments on the left'''

__version__ = '2023.4.15'

__all__ = ['leftdefault']


from functools import wraps, cached_property, partial
from inspect import Signature as _Signature
from types import MappingProxyType


class Signature(_Signature):
    left_default_skip = 0

    @cached_property
    def left_default_splits(self):
        i, j = self.left_default_skip, None
        for k, par in enumerate(super().parameters.values()):
            if k < i:
                continue
            if par.kind != par.POSITIONAL_ONLY:
                break
            if par.default != par.empty and j is None:
                j = k
        if j is None:
            j = k
        if i > k:
            i = k
        return i, j, k

    @cached_property
    def parameters(self):
        pars = super().parameters
        names = list(pars.keys())
        i, j, k = self.left_default_splits
        return MappingProxyType({name: pars[name]
                                 for name in [*names[:i], *names[j:k],
                                              *names[i:j], *names[k:]]})


def leftdefault(func=None, *, skip=0):
    if func is None:
        return partial(leftdefault, skip=skip)

    sig = Signature.from_callable(func)
    sig.left_default_skip = skip
    i, j, k = sig.left_default_splits
    n = j-i

    @wraps(func)
    def wrapper(*args, **kwargs):
        skip, pos, rest = args[:i], args[i:k], args[k:]
        return func(*skip, *pos[-n:], *pos[:-n], *rest, **kwargs)

    wrapper.__signature__ = sig

    return wrapper
