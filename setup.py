#!/usr/bin/env python

from distutils.core import setup

setup(name='papers',
      version='1',
      author='Fabien Benureau, Olivier Mangin',
      author_email='fabien.benureau+inria@gmail.com',
      url='',
      description='research papers manager',
      requires=['pybtex'],
      packages = ['papers', 'papers.commands'],
      scripts=['papers/papers']
      )
