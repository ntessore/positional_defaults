# license: MIT
'''Set defaults for any positional-only parameter.'''

__version__ = '2023.4.18'

__all__ = ['defaults']

from functools import partial
from inspect import Parameter, Signature as _Signature
from types import MappingProxyType
from typing import Any, Callable, List, Tuple, TypeVar, Union, overload

from _positional_defaults import ARG, wrap

F = TypeVar('F', bound=Callable[..., Any])


class Signature(_Signature):
    '''Signature with defaults anywhere in positional-only parameters.'''

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__parameters = super().parameters

    def update_defaults(self, **defaults: object) -> None:
        '''Set default values anywhere in the positional-only parameters.'''
        parameters = {**super().parameters}
        for name, default in defaults.items():
            try:
                par = parameters[name]
            except KeyError:
                raise ValueError(f'unknown parameter "{name}"') from None
            if par.kind != par.POSITIONAL_ONLY:
                raise ValueError(f'parameter "{name}" is not positional-only')
            parameters[name] = par.replace(default=default)
        self.__parameters = MappingProxyType(parameters)

    @property
    def parameters(self) -> 'MappingProxyType[str, Parameter]':
        return self.__parameters


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
    sig.update_defaults(**_defaults)

    pars = {name: par for name, par in sig.parameters.items()
            if par.kind == par.POSITIONAL_ONLY}

    n = len(pars)

    fill_order = [name for name in pars if name not in _defaults]
    fill_order += list(_defaults.keys())

    part_order = [[name for name in pars if name in fill_order[:k]]
                  for k in range(n+1)]

    _patterns: List[Tuple[object, ...]] = []
    for k in range(n+1):
        pattern: List[object] = []
        for name in pars:
            if name in part_order[k]:
                pattern.append(ARG)
            elif name in _defaults:
                pattern.append(_defaults[name])
            else:
                break
        _patterns.append(tuple(pattern))
    patterns: Tuple[Tuple[object, ...], ...] = tuple(_patterns)

    wrapper = wrap(func, patterns)
    wrapper.__signature__ = sig  # type: ignore[attr-defined]

    return wrapper
