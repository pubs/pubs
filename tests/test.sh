#!/usr/bin/env bash
rm -Rf tmpdir/*;
pubs init -p tmpdir/;
pubs add -d data/pagerank.pdf -b data/pagerank.bib;
pubs list;
pubs tag;
pubs tag Page99 network+search;
pubs tag Page99;
pubs tag search;
pubs tag 0;
#rm -Rf tmpdir/*;
