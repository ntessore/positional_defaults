# type: ignore

from functools import wraps
from timeit import repeat

from positional_defaults import defaults


def decorated(func):
    '''Comparison: only call function with args & kwargs.'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def test_performance(*funcs, **repeat_kwargs):
    '''Test the performance of the passed functions.'''
    results = []
    for func in funcs:
        times = repeat(func, **repeat_kwargs)
        results.append((func.__name__, times))
    return results


def func0():
    '''Function with no arguments, doing nothing.'''
    pass


def func1(a1=None, /):
    '''Function with one argument, doing nothing.'''
    pass


def func5(a1=None, a2=None, a3=None, a4=None, a5=None, /):
    '''Function with five arguments, doing nothing.'''
    pass


func0_decorated = decorated(func0)
func0_decorated.__name__ = 'func0_decorated'

func0_defaults = defaults(func0)
func0_defaults.__name__ = 'func0_defaults'

func1_decorated = decorated(func1)
func1_decorated.__name__ = 'func1_decorated'

func1_defaults = defaults(func1)
func1_defaults.__name__ = 'func1_defaults'

func5_decorated = decorated(func5)
func5_decorated.__name__ = 'func5_decorated'

func5_defaults = defaults(func5)
func5_defaults.__name__ = 'func5_defaults'

results = test_performance(
    func0, func0_decorated, func0_defaults,
    func1, func1_decorated, func1_defaults,
    func5, func5_decorated, func5_defaults,
)

for name, times in results:
    print(f'{name:19}', sum(times)/len(times))
