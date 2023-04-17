positional_defaults
===================

**Python package to set defaults for any positional-only parameter**

This tiny Python package contains a decorator `@defaults` which lets you
specify default arguments for any positional-only parameter, no matter where
it appears in the argument list.

Installation
------------

    pip install positional_defaults

Usage
-----

Use the `@defaults` decorator to set default values for positional-only
parameters (i.e. those before the positional-only indicator `/`):

```py
from positional_defaults import defaults

@defaults(start=0)
def myrange(start, stop, /, step=1):
    ...

# now these are equivalent
myrange(4)
myrange(0, 4)
myrange(0, 4, 1)
```

This works on methods as well:

```py
class A:
    @defaults(start=0)
    def myrange(self, start, stop, /, step=1):
        ...
```

Multiple defaults can be set, which are filled in the order in which they are
specified:

```py
@defaults(forename='Alice', greeting='Welcome', prefix='Mrs')
def greet(greeting, prefix, forename, surname, /, suffix='Esq'):
    ...

# these are now equivalent
greet('Smith')
greet('Alice', 'Smith')
greet('Welcome', 'Alice', 'Smith')
greet('Welcome', 'Mrs', 'Alice', 'Smith')
greet('Welcome', 'Mrs', 'Alice', 'Smith', 'Esq')
```

Signatures
----------

Left-defaulted functions come with the correct signature:

```py
>>> from inspect import signature
>>> signature(myrange)
<Signature (start=0, stop, /, step=1)>
>>> signature(greet)
<Signature (greeting='Welcome', prefix='Mrs', forename='Alice', surname, /, suffix='Esq')>
```

These show up correctly in the usual places such as `help()`:

```py
>>> help(interval)

Help on function myrange:

myrange(start=0, stop, /, step=1)

>>> help(greet)

Help on function greet:

greet(greeting='Welcome', prefix='Mrs', forename='Alice', surname, /, suffix='Esq')

```
