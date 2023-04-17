# type: ignore

from functools import wraps
from inspect import signature
from timeit import repeat

from positional_defaults import defaults


def nodefaults(func):
    '''Comparison: only call function with args & kwargs.'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def test_performance(*funcs, **repeat_kwargs):
    '''Test the performance of the passed functions.'''
    results = []
    for func in funcs:
        name = func.__name__
        sig = signature(func)
        nargs = len(sig.parameters)
        stmt = f'{name}{tuple(range(nargs))}'
        times = repeat(stmt, globals=globals(), **repeat_kwargs)
        results.append((name, times))
    return results


def func1(a, /):
    '''Function with one argument, doing nothing.'''
    pass


def func5(a, b, c, d, e, /):
    '''Function with five arguments, doing nothing.'''
    pass


func1_nodefaults = nodefaults(func1)
func1_nodefaults.__name__ = 'func1_nodefaults'

func1_defaults = defaults(func1, a=None)
func1_defaults.__name__ = 'func1_defaults'

func5_nodefaults = nodefaults(func5)
func5_nodefaults.__name__ = 'func5_nodefaults'

func5_defaults = defaults(func5, a=None, d=None)
func5_defaults.__name__ = 'func5_defaults'

results = test_performance(
    func1, func1_nodefaults, func1_defaults,
    func5, func5_nodefaults, func5_defaults,
)

for name, times in results:
    print(f'{name:19}', sum(times)/len(times))
