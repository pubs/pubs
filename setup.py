#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pubs',
      version='4',
      author='Fabien Benureau, Olivier Mangin, Jonathan Grizou',
      author_email='fabien.benureau+inria@gmail.com',
      url='',
      description='research papers manager',
      requires=['bibtexparser'],
      packages=find_packages(),
      package_data={'': ['*.tex', '*.sty']},
      scripts=['pubs/pubs']
      )

# TODO include proper package data from plugins (08/06/2013)
# should we use MANIFEST.in or package_data = ..., or both
