#! /bin/bash
cwd="ABS-PATH-TO/PP-20_MM-80"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-20_MM-80.log
#mv $cwd/PP-20_MM-80.log $cwd/PP-20_MM-80.bac

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
