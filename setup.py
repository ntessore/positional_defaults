# type: ignore

import sys
import os
from setuptools import setup

py_modules = ['positional_defaults', '_positional_defaults']
ext_modules = []
setup_requires = []

use_mypyc = False

if '--use-mypyc' in sys.argv:
    sys.argv.remove('--use-mypyc')
    use_mypyc = True
elif os.getenv('USE_MYPYC', None) is not None:
    use_mypyc = True

if use_mypyc:
    try:
        from mypyc.build import mypycify
    except ModuleNotFoundError:
        setup_requires.append('mypy')
    else:
        py_modules.remove('_positional_defaults')
        ext_modules = mypycify(['_positional_defaults.py'])

setup(py_modules=py_modules,
      ext_modules=ext_modules,
      setup_requires=setup_requires)
