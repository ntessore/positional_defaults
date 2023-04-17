# type: ignore

import sys
from setuptools import setup

py_modules = ['positional_defaults', '_positional_defaults']
ext_modules = []

if len(sys.argv) > 1 and '--use-mypyc' in sys.argv:
    sys.argv.remove('--use-mypyc')

    from mypyc.build import mypycify

    py_modules.remove('positional_defaults')
    ext_modules = mypycify(['positional_defaults.py'])

setup(py_modules=py_modules, ext_modules=ext_modules)
