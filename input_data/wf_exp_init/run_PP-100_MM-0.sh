#! /bin/bash
cwd="ABS-PATH-TO/PP-100_MM-0"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-100_MM-0.log
#mv $cwd/PP-100_MM-0.log $cwd/PP-100_MM-0.bac

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
