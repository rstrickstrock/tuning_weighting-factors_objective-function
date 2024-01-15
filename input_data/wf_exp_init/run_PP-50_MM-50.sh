#! /bin/bash
cwd="ABS-PATH-TO/PP-50_MM-50"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-50_MM-50.log
#mv $cwd/PP-50_MM-50.log $cwd/PP-50_MM-50.bac

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
