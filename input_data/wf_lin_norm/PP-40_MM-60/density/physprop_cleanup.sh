#! /bin/bash
result_cwd=$1

for file in $result_cwd/*.trr
do
    rm $file
done
