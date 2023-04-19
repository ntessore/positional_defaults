'''Implementation of the positional_defaults package.'''

from typing import Any, Callable, Tuple


def wrap(
    wrapped: Callable[..., Any],
    patterns: Tuple[Tuple[object, ...], ...],
    placeholder: object,
) -> Callable[..., Any]:
    if type(patterns) is not tuple:
        raise TypeError('patterns must be tuple')

    for i, pattern in enumerate(patterns):
        if type(pattern) is not tuple:
            raise TypeError(f'patterns[{i}] must be tuple')

        nargs = sum(obj is placeholder for obj in pattern)
        if nargs != i:
            raise ValueError(f'patterns[{i}] must contain placeholder {i}'
                             f'times (found {nargs})')

    def wrapper(*args: object, **kwargs: object) -> Any:
        if len(args) < len(patterns):
            pattern = patterns[len(args)]
            aiter = iter(args)
            args = tuple(next(aiter) if a is placeholder else a
                         for a in pattern)
        return wrapped(*args, **kwargs)

    return wrapper
