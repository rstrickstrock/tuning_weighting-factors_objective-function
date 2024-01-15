#! /bin/bash
cwd="ABS-PATH-TO/PP-05_MM-95"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-05_MM-95.log

miscffoptiw="python ../../FFLOW//main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
