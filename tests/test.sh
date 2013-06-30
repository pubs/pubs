#!/usr/bin/env bash
rm -Rf paper_test/*;
papers init -p paper_test/;
papers add -d data/pagerank.pdf -b data/pagerank.bib;
papers list;
papers tag;
papers tag Page99 network+search;
papers tag Page99;
papers tag search;
papers tag 0;
rm -Rf paper_test/*;
