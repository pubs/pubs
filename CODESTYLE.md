Generally
=========

Use use regular coding style:
http://www.python.org/dev/peps/pep-0008/
http://google-styleguide.googlecode.com/

One can break those rules if the situation requires it. Keep it contained.


Some specific rules for this package :

Git
===

This project use git-flow {nvie.com/posts/a-successful-git-branching-model}
as a model for branches management. In particular :
1. master is for release only
2. when you commit to develop, run nosetests before. All tests should pass.
3. when you commit to develop, run nosetests before. All tests should pass.
4. when you commit to develop, run nosetests before. All tests should pass.
5. in 'feat/' branches, you do whatever you want.
6. when developping a new feature, write tests for it.


Alignement
==========

We strive for code clarity first, and then conformance to pep-8.
As such, any code alignement that make the code clearer, easier to use,
edit and debug takes precedence over proper spacing.


Strings
=======

For literals strings, ' is preferred to ", but use " when the string contains '.

yes: "run the command 'flake8' before committing"
no : 'run the command \'flake8\' before committing'


Use '.format' syntax for strings, and '+' only when the use calls it.
Don't mix and match.

yes: s = color + s + end
yes: '{}: file {} could not be read'.format(errorname, filepath)
no : errorname + ': file {} could not be read'.format(filepath)


Names
=====

Avoid at all cost to name a variable like a module from the package, a
dependency or the standart lib.
This breaks coherence across the code, makes it harder to read.
Change either the module or variable name.


Function that have only local uses should be preceded by an underscore.

yes: def _auxiliary_local_fun():
         pass
no : def auxiliary_local_fun():
         pass

These functiona won't be imported automatically with the module.
It keeps the interface clean, makes occasional hacks explicit, and inform other
developers that theses functions may need special care when uses outside their
natural habitat.


Files
=====

Unless you have a good reason, use 'open' as such :
yes: with open(path, 'w') as f:
         f.read()
no : f = open(path, 'r')
         f.read()
     f.close()
