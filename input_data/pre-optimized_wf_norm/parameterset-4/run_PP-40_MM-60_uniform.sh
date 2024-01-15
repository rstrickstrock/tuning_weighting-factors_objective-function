#! /bin/bash
cwd="ABS-PATH-TO/PP-40_MM-60_uniform"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
#mv $cwd/PP-40_MM-60*.log $cwd/PP-40_MM-60*.bac
rm $cwd/PP-40_MM-60*.log

miscffoptiw="python ../../../FFLOW/main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
