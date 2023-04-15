"""Support for default arguments on the left."""

from __future__ import annotations

from functools import cached_property, wraps
from inspect import Parameter as _Parameter
from inspect import Signature as _Signature
from types import MappingProxyType
from typing import TYPE_CHECKING, ParamSpec, TypeVar, overload

__version__ = "2023.4.15"
__all__ = ["leftdefault"]

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")
R = TypeVar("R")


class LeftDefaultSignature(_Signature):
    """Signature that reverses the order of positional-only arguments.

    This is a workaround for the fact that default arguments must be
    on the right.

    Attributes
    ----------
    left_default_skip : int
        Number of positional-only arguments to skip when moving
        positional-only arguments.
    """

    left_default_skip: int = 0

    @cached_property
    def left_default_splits(self) -> tuple[int, int, int]:
        """Index the positional-only arguments into (skip, mandatory, optional)."""
        i, j, k = self.left_default_skip, None, 0
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
    def parameters(self) -> MappingProxyType[str, _Parameter]:
        """Parameters with positional-only arguments moved to the left."""
        pars = super().parameters
        names = list(pars.keys())
        i, j, k = self.left_default_splits
        return MappingProxyType(
            {
                name: pars[name]
                for name in (*names[:i], *names[j:k], *names[i:j], *names[k:])
            },
        )


class LeftDefaultDecorator:
    """Decorator to move default arguments to the left."""

    __slots__ = ("skip",)

    def __init__(self, skip: int) -> None:
        """Initialize."""
        self.skip = skip

    def __call__(self, func: Callable[P, R], /) -> Callable[P, R]:
        """Decorate a function."""
        sig = LeftDefaultSignature.from_callable(func)
        sig.left_default_skip = self.skip
        i, j, k = sig.left_default_splits
        n = j - i

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            skip, pos, rest = args[:i], args[i:k], args[k:]
            return func(*skip, *pos[-n:], *pos[:-n], *rest, **kwargs)  # type: ignore[arg-type]  # noqa: E501

        object.__setattr__(wrapper, "__signature__", sig)

        return wrapper


@overload
def leftdefault(func: Callable[P, R], /) -> Callable[P, R]:
    ...


@overload
def leftdefault(func: None = ..., /) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def leftdefault(
    func: Callable[P, R] | None = None, /, *, skip: int = 0
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Move decorated function's positional-only default arguments to the left.

    Parameters
    ----------
    func : Callable[P, R], optional
        Function for which the positional-only default arguments should precede
        the non-default arguments.
    skip : int, optional
        Number of positional-only arguments to skip when moving.

    Returns
    -------
    Callable[P, R], Callable[[Callable[P, R]], Callable[P, R]]
        Decorated function or decorator, if `func` is `None`.

    Examples
    --------
    >>> @leftdefault
    ... def myrange(stop, start=0, /, step=1):
    ...     return (start, stop, step)

    Now these are equivalent:
    >>> myrange(4)
    (0, 4, 1)
    >>> myrange(0, 4)
    (0, 4, 1)
    >>> myrange(0, 4, 1)
    (0, 4, 1)
    """
    decorator = LeftDefaultDecorator(skip)
    if func is None:  # equivalent to partial
        return decorator
    return decorator(func)
