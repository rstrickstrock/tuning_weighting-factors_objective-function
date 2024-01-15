#! /bin/bash
cwd="ABS-PATH-TO/PP-80_MM-20"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-80_MM-20.log
#mv $cwd/PP-80_MM-20.log $cwd/PP-80_MM-20.bac

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
