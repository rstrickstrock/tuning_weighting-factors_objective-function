#!/bin/bash

head='sed '
substitute=''
tudels='" '

tail=' ExTrM.template.dat > bindir/06_mm_opt/ExTrM.Amber.hydrocarbons.dat'
index=1

for par in $@; do

	substitute="$substitute $sed s/X_$index/$par/;"
	index=`expr $index + 1` 


done

eval $head$tudels$substitute$tudels$tail

