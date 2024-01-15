#! /bin/bash
result_cwd=$1"/output/"

cat $result_cwd"/Energy.rel.extrm.txt" | cut -f2 -d ' '

