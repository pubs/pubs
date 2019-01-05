if [ "$TEST_MODE" = "TEST" ]; then
  PUBS_TESTS_MODE=MOCK python setup.py test;
  if [ "$TO_TEST" = "FULL" ]; then PUBS_TESTS_MODE=COLLECT python setup.py test; fi;
fi

if [ "$TEST_MODE" = "INSTALL" ]; then
  pip install pubs;
  pubs --help;
  pip uninstall -y pubs;
fi
