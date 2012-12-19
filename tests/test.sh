#!/usr/bin/env bash
rm -Rf .papers;
papers init;
papers list;
papers add data/pagerank.pdf data/pagerank.bib;
papers list;
papers open 0;
papers open Page99;
rm -Rf .papers;
