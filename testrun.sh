#!/bin/sh
rm ./output-example.html
python3 ./md2html.py ./entry-example.md
cat ./output-example.html
