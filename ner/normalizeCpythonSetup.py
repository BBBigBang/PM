#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
# *************************************************
# > File Name: normalizeCpythonSetup.py
# > Author: yang 
# > Mail: yangperasd@163.com 
# > Created Time: Mon 20 Nov 2017 09:24:33 AM CST
# *************************************************
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

ext_modules=[
    Extension(
        'normalizeCpython',
        ['normalizeCpython.pyx'],
        include_dirs=['/usr/local/lib/python2.7/dist-packages/numpy/core/include/'],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
        )
]

setup(
    name='normalizeCpython-parallel',
    ext_modules=cythonize(ext_modules),
    )
