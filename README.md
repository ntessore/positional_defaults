leftdefault
===========

**Python package to put default before non-default arguments**

This tiny Python package contains a decorator `@leftdefault` which moves
positional-only default arguments to the beginning of the function signature.

Installation
------------

    pip install leftdefault

Usage
-----

Simply decorate functions with `@leftdefault` and delimit the arguments with
the positional-only indicator `/`:

```py
from leftdefault import leftdefault

@leftdefault
def myrange(stop, start=0, /, step=1):
    return (start, stop, step)

# now these are equivalent
myrange(4)
myrange(0, 4)
myrange(0, 4, 1)
```

Multiple default arguments can be moved to the left, they are filled from first
to last as usual:

```py
@leftdefault
def puttext(text, x=0., y=1., /, *args, **kwargs):
    return (x, y, text)

# now these are equivalent
puttext('hi')
puttext(0., 'hi')
puttext(0., 1., 'hi')
```

The `@leftdefault` decorator can take an optional `skip=N` keyword argument to
indicate that `N` initial positional-only arguments should be skipped.  This is
necessary for methods with `self`:

```py
class A:
    @leftdefault(skip=1)
    def rangemethod(self, stop, start=0, /, step=1):
        return (start, stop, step)
```

Inspection
----------

Left-defaulted functions come with the correct signature:

```py
>>> from inspect import signature
>>> signature(myrange)
<Signature (start=0, stop, /, step=1)>
>>> signature(puttext)
<Signature (x=None, y=None, text, /, *args, **kwargs)>
>>> signature(A.rangemethod)
<Signature (self, start=0, stop, /, step=1)>
```

These show up correctly in the usual places such as `help()`:

```py
>>> help(interval)

Help on function myrange:

myrange(start=0, stop, /, step=1)

>>> help(A.interval)

Help on function puttext:

puttext(x=None, y=None, text, /, *args, **kwargs)

```
