#!/usr/bin/env bash
papers init;
papers list;
papers add data/pagerank.pdf data/pagerank.bib;
papers list;
papers open 0;
rm -Rf .papers;