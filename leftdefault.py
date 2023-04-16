# license: MIT
'''Support for default arguments on the left'''

__version__ = '2023.4.16'

__all__ = ['leftdefault']

from functools import wraps, cached_property, partial
from inspect import Parameter, Signature as _Signature
from types import MappingProxyType
from typing import Any, Callable, List, Sequence, Tuple, TypeVar, Union
from typing import overload

F = TypeVar('F', bound=Callable[..., Any])


class Signature(_Signature):
    '''Signature that reverses the order of positional-only arguments.

    This is a workaround for the fact that default arguments must be on
    the right.

    '''

    left_default_skip: int = 0
    left_default_which: Union[Sequence[str], None] = None

    @cached_property
    def left_default_splits(self) -> Tuple[int, int, int,
                                           Union[List[Tuple[int, ...]], None]]:
        '''Take the list of positional-only arguments and return indices
        i, j, k such that
            - args[:i] are skipped over,
            - args[i:j] are required, and
            - args[j:k] are optional.
        '''

        which = self.left_default_which
        if which is not None:
            base_order = []

        i = k = self.left_default_skip
        j = -1
        for k, par in enumerate(super().parameters.values()):
            if k < i:
                continue
            if par.kind != par.POSITIONAL_ONLY:
                break
            if par.default != par.empty:
                if j == -1:
                    j = k
                if which is not None:
                    try:
                        base_order.append(which.index(par.name))
                    except ValueError:
                        break
        if j == -1:
            j = k
        if i > k:
            i = k

        # precompute the sort order for all optional argument counts
        if which is not None:
            inv = sorted(range(len(base_order)), key=base_order.__getitem__)
            order = []
            for n in range(len(inv)+1):
                n_inv = [m for m in inv if m < n]
                n_order = sorted(range(n), key=n_inv.__getitem__)
                order.append(tuple(n_order))
            assert order[-1] == tuple(base_order)
        else:
            order = None

        return i, j, k, order

    @cached_property
    def parameters(self) -> MappingProxyType[str, Parameter]:
        '''Reordered parameters list with left-defaults.'''
        pars = super().parameters
        names = list(pars.keys())
        i, j, k, order = self.left_default_splits
        optnames = names[j:k]
        if order is not None:
            optnames = [name for _, name in sorted(zip(order[-1], optnames))]
        return MappingProxyType({name: pars[name]
                                 for name in (*names[:i], *optnames,
                                              *names[i:j], *names[k:])})


@overload
def leftdefault(func: F, /, *,
                skip: int = 0,
                which: Union[str, Sequence[str], None] = None,
                ) -> F:
    ...


@overload
def leftdefault(func: None, /, *,
                skip: int = 0,
                which: Union[str, Sequence[str], None] = None,
                ) -> Callable[[F], F]:
    ...


def leftdefault(func: Any = None, /, *,
                skip: int = 0,
                which: Union[str, Sequence[str], None] = None,
                ) -> Any:
    '''Move positional-only default arguments to the left.'''
    if func is None:
        return partial(leftdefault, skip=skip, which=which)

    if not callable(func):
        raise TypeError('func must be callable')

    if isinstance(which, str):
        which = tuple(map(str.strip, which.split(',')))

    sig = Signature.from_callable(func)
    sig.left_default_skip = skip
    sig.left_default_which = which
    i, j, k, order = sig.left_default_splits
    n = j - i

    if order is None:
        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> Any:
            skip, pos, rest = args[:i], args[i:k], args[k:]
            return func(*skip, *pos[-n:], *pos[:-n], *rest, **kwargs)
    else:
        x: List[Tuple[int, ...]] = order

        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> Any:
            skip, pos, rest = args[:i], args[i:k], args[k:]
            opt = pos[:-n]
            return func(*skip, *pos[-n:], *(opt[o] for o in x[len(opt)]),
                        *rest, **kwargs)

    wrapper.__signature__ = sig  # type: ignore[attr-defined]

    return wrapper
