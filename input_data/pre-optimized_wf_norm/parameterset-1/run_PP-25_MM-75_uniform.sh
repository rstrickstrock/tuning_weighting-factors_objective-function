#! /bin/bash
cwd="ABS-PATH-TO/PP-25_MM-75_uniform"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-25_MM-75.log

miscffoptiw="python ../../../FFLOW/main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
