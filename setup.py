#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pubs',
      version='4',
      author='Fabien Benureau, Olivier Mangin, Jonathan Grizou',
      author_email='fabien.benureau+inria@gmail.com',
      url='',
      description='research papers manager',
      requires=['pyyaml', 'bibtexparser', 'dateutil'],
      packages=find_packages(),
      scripts=['pubs/pubs']
      )
