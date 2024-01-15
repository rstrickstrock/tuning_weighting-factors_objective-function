#! /bin/bash
cwd="ABS-PATH-TO/PP-60_MM-40"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-60_MM-40.log
#mv $cwd/PP-60_MM-40.log $cwd/PP-60_MM-40.bac

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
