#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='papers',
      version='1',
      author='Fabien Benureau, Olivier Mangin',
      author_email='fabien.benureau+inria@gmail.com',
      url='',
      description='research papers manager',
      requires=['pybtex'],
      packages=find_packages(),
      scripts=['papers/papers']
      )

# TODO include package data from plugins
# Jonathan could not make it works (08/06/2013)
# should we use MANIFEST.in or package_data = ..., or both
