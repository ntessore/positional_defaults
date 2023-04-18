'''Implementation details of the positional_defaults package.'''

from inspect import Parameter, Signature as _Signature
from typing import Any
from types import MappingProxyType


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
    def parameters(self) -> MappingProxyType[str, Parameter]:
        return self.__parameters
