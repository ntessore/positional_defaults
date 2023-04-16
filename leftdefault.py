# license: MIT
'''Support for default arguments on the left'''

__version__ = '2023.4.16'

__all__ = ['leftdefault']

from functools import wraps, cached_property, partial
from inspect import Parameter, Signature as _Signature
from types import MappingProxyType
from typing import Any, Callable, Tuple, TypeVar, overload

F = TypeVar('F', bound=Callable[..., Any])


class Signature(_Signature):
    '''Signature that reverses the order of positional-only arguments.

    This is a workaround for the fact that default arguments must be on
    the right.

    '''

    left_default_skip: int = 0

    @cached_property
    def left_default_splits(self) -> Tuple[int, int, int]:
        '''Take the list of positional-only arguments and return indices
        i, j, k such that
            - args[:i] are skipped over,
            - args[i:j] are required, and
            - args[j:k] are optional.
        '''
        i = k = self.left_default_skip
        j = -1
        for k, par in enumerate(super().parameters.values()):
            if k < i:
                continue
            if par.kind != par.POSITIONAL_ONLY:
                break
            if par.default != par.empty and j == -1:
                j = k
        if j == -1:
            j = k
        if i > k:
            i = k
        return i, j, k

    @cached_property
    def parameters(self) -> MappingProxyType[str, Parameter]:
        '''Reordered parameters list with left-defaults.'''
        pars = super().parameters
        names = list(pars.keys())
        i, j, k = self.left_default_splits
        return MappingProxyType({name: pars[name]
                                 for name in (*names[:i], *names[j:k],
                                              *names[i:j], *names[k:])})


@overload
def leftdefault(func: F, /, *, skip: int = 0) -> F:
    ...


@overload
def leftdefault(func: None, /, *, skip: int = 0) -> Callable[[F], F]:
    ...


def leftdefault(func: Any, /, *, skip: Any = 0) -> Any:
    '''Move positional-only default arguments to the left.'''
    if func is None:
        return partial(leftdefault, skip=skip)

    if not callable(func):
        raise TypeError('func must be callable')

    sig = Signature.from_callable(func)
    sig.left_default_skip = skip
    i, j, k = sig.left_default_splits
    n = j - i

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        skip, pos, rest = args[:i], args[i:k], args[k:]
        return func(*skip, *pos[-n:], *pos[:-n], *rest, **kwargs)

    wrapper.__signature__ = sig  # type: ignore[attr-defined]

    return wrapper
