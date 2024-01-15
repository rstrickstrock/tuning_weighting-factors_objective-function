#! /bin/bash
cwd="ABS-PATH-TO/PP-40_MM-60"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-40_MM-60.log
#mv $cwd/PP-40_MM-60.log $cwd/PP-40_MM-60.bac

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
