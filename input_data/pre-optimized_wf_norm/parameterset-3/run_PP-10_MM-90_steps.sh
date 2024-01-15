#! /bin/bash
cwd="ABS-PATH-TO/PP-10_MM-90_steps"
if [[ -d $cwd/PhysProp ]]; then
  rm -rf $cwd/PhysProp
fi
if [[ -d $cwd/QMMM ]]; then
  rm -rf $cwd/QMMM
fi
rm $cwd/PP-10_MM-90.log

miscffoptiw="python ../../../FFLOW/main.py"

$miscffoptiw $cwd/octane_hybrid_new.cfg -d
