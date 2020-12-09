#!/bin/sh
rm ./entry-example.html
python3 ./md2html.py ./entry-example.md
cat ./entry-example.html
