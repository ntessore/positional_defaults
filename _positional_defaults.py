'''Implementation details of the positional_defaults package.'''

from functools import wraps
from typing import Any, Callable, Tuple

ARG = object()


def fill(pattern: Tuple[object, ...], args: Tuple[object, ...],
         ) -> Tuple[object, ...]:
    '''Replace ARG with args in pattern and concatenate rest of args.'''
    k = -1
    return (tuple(args[(k := k+1)] if a is ARG else a for a in pattern)
            + args[k+1:])


def wrap(wrapped: Callable[..., Any],
         patterns: Tuple[Tuple[object, ...], ...],
         ) -> Callable[..., Any]:
    '''Create a wrapper that fills in args based on pattern.'''
    n = len(patterns) - 1

    @wraps(wrapped)
    def wrapper(*args: object, **kwargs: object) -> Any:
        return wrapped(*fill(patterns[min(len(args), n)], args), **kwargs)

    return wrapper
