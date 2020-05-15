#!/bin/bash

temp='./config/populate_foodon.ini'

for alpha in '0.0' '0.1' '0.2' '0.3' '0.4' '0.5' '0.6' '0.7' '0.8' '0.9' '1.0' ;
do
    for num_mapping in '7748';
    do
        configfile="./config/populate_foodon_alpha"$alpha"_n"$num_mapping".ini"
        cp './config/populate_foodon.ini' $configfile

        sed -i 's|alpha = alpha_replace|alpha = '$alpha'|g' $configfile
        sed -i 's|num_mapping_per_iteration = num_mapping_replace|num_mapping_per_iteration = '$num_mapping'|g' $configfile

        logfile="populate_foodon_alpha"$alpha"_n"$num_mapping".log"
        sed -i 's|populate_foodon.log|'$logfile'|g' $configfile

        sed -i 's|'$temp'|'$configfile'|g' ./script.slurm

        sleep 1s
        sbatch script.slurm
        sleep 1s

        temp=$configfile
    done
done

