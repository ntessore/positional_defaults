# license: MIT
'''Set defaults for any positional-only parameter.'''

__version__ = '2023.4.17'

__all__ = ['defaults']

from functools import partial, wraps
from typing import Any, Callable, List, Tuple, TypeVar, Union, overload

from _positional_defaults import Signature

F = TypeVar('F', bound=Callable[..., Any])


@overload
def defaults(func: None, /, **_defaults: object) -> Callable[[F], F]:
    ...


@overload
def defaults(func: F, /, **_defaults: object) -> F:
    ...


def defaults(func: Union[F, None] = None, /, **_defaults: object) -> Any:
    '''Set defaults for any positional-only parameter.'''

    if func is None:
        return partial(defaults, **_defaults)

    if not callable(func):
        raise TypeError('not a callable')

    sig = Signature.from_callable(func)
    sig.update_defaults(**_defaults)

    pars = {name: par for name, par in sig.parameters.items()
            if par.kind == par.POSITIONAL_ONLY}

    n = len(pars)

    default_order = [par.name for par in pars.values()
                     if par.default != par.empty]

    fill_order = [name for name in pars if name not in default_order]
    fill_order += list(_defaults.keys())
    fill_order += [name for name in default_order if name not in _defaults]

    part_order = [[name for name in pars if name in fill_order[:k]]
                  for k in range(n+1)]

    where: List[Tuple[Tuple[int, int], ...]] = []
    for k in range(n+1):
        tmp: List[Tuple[int, int]] = []
        for name in pars:
            if name in part_order[k]:
                index = (0, part_order[k].index(name))
            elif name in default_order:
                index = (1, default_order.index(name))
            else:
                break
            tmp.append(index)
        where.append(tuple(tmp))

    wrapped: F = func

    __defaults__ = tuple(par.default for par in pars.values()
                         if par.default != par.empty)

    @wraps(wrapped)
    def wrapper(*args: object, **kwargs: object) -> Any:
        a = (args, __defaults__)
        args = tuple(a[i][j] for i, j in where[min(len(args), n)]) + args[n:]
        return wrapped(*args, **kwargs)

    wrapper.__signature__ = sig  # type: ignore[attr-defined]

    return wrapper
