# license: MIT
'''Set defaults for any positional-only parameter.'''

__version__ = '2023.4.19'

__all__ = ['defaults']

from functools import partial, update_wrapper
from inspect import Signature
from typing import Any, Callable, TypeVar, Union, overload

from _positional_defaults import wrap

F = TypeVar('F', bound=Callable[..., Any])


ARG = object()


class DefaultsSignature(Signature):
    '''Signature for defaults anywhere in the positional-only parameters.'''

    __slots__ = ()

    def __init__(self, *args: Any, **kwargs: Any,
                 ) -> None:
        if '__validate_parameters__' not in kwargs:
            kwargs['__validate_parameters__'] = False
        super().__init__(*args, **kwargs)


@overload
def defaults(func: None, /, **_defaults: object) -> Callable[[F], F]:
    ...


@overload
def defaults(func: F, /, **_defaults: object) -> F:
    ...


def defaults(func: Union[F, None] = None, /, **_defaults: object
             ) -> Any:
    '''Set defaults for any positional-only parameter.'''

    if func is None:
        return partial(defaults, **_defaults)

    if not callable(func):
        raise TypeError('not a callable')

    sig = Signature.from_callable(func)

    posonly = [name for name, par in sig.parameters.items()
               if par.kind == par.POSITIONAL_ONLY]

    if (missing := _defaults.keys() - posonly):
        raise ValueError('not a positional-only parameter: '
                         + ', '.join(missing))

    fill_order = [name for name in posonly if name not in _defaults]
    fill_order += list(_defaults.keys())

    part_order = [[name for name in posonly if name in fill_order[:n]]
                  for n in range(len(posonly))]

    patterns = []
    for names in part_order:
        pattern = []
        for name in posonly:
            if name in names:
                pattern.append(ARG)
            elif name in _defaults:
                pattern.append(_defaults[name])
            else:
                break
        patterns.append(tuple(pattern))

    wrapper = wrap(func, tuple(patterns), ARG)
    update_wrapper(wrapper, func)

    pars = [par.replace(default=_defaults.get(par.name, par.default))
            for par in sig.parameters.values()]
    newsig = DefaultsSignature(pars, return_annotation=sig.return_annotation)

    wrapper.__signature__ = newsig  # type: ignore[attr-defined]

    return wrapper
