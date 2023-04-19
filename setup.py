# type: ignore

import sys
import os
from setuptools import setup, Extension

py_modules = ['positional_defaults', '_positional_defaults']
ext_modules = []

use_extension = False

if '--compile-extension' in sys.argv:
    sys.argv.remove('--compile-extension')
    use_extension = True
elif os.getenv('COMPILE_POSITIONAL_DEFAULTS', None) is not None:
    use_extension = True

if use_extension:
    py_modules.remove('_positional_defaults')
    ext_modules.append(Extension('_positional_defaults',
                                 ['_positional_defaults.c']))

setup(py_modules=py_modules,
      ext_modules=ext_modules)
