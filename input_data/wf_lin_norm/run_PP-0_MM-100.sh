#! /bin/bash
cwd="ABS-PATH-TO/PP-0_MM-100"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-0_MM-100.log
#mv $cwd/PP-0_MM-100.log $cwd/PP-0_MM-100.bac

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
