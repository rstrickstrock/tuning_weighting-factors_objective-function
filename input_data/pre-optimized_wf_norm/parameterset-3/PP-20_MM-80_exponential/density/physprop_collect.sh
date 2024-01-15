#! /bin/bash
result_cwd=$1

for file in $result_cwd/slurm-*
do
    last_line=$(tail -1 $file)
    #echo $last_line
    if [[ $last_line == *"Density"* ]]
    then
        read -a strarr <<< $last_line
        #for item in "${strarr[@]}"
        #do
        #    echo $item
        #done
        echo ${strarr[1]}   #density value
        #echo ${strarr[-1]}  #unit
    fi
done
