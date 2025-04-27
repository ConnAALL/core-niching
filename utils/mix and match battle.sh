#!/usr/bin/bash

# What we do here is battle agents niched to an enviornment with agents niched to another enviornment

# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR="$(dirname "$SCRIPT_DIR")"
# Set the number of instances you want to run
num_instances_per_team=30;
split=15;


for ((j = 1; j <= 4; j++)); do	
	# 1 not headless so we can see whats going on
	python3 "$REPO_DIR/src/testing_fitness.py" "Q"$j"_"$split "headless_false" $j&
	for ((i = 1; i <= split-1; i++)); do
	    echo "Running instance $i"
	    python3 "$REPO_DIR/src/testing_fitness.py" "Q"$j"_"$i "headless_true" $j&
	    sleep 0.75;
	done
done

for ((j = 1; j <= 4; j++)); do	
    	k=$(( (j % 4) + 1 ))
	k_enemy=$(( k + 4 ))
	python3 "$REPO_DIR/src/testing_fitness.py" "Q"$j"_"$num_instances_per_team "headless_false" $k_enemy&
	for ((i = split; i <= num_instances_per_team -1; i++)); do
	    echo "Running instance $i"
	    python3 "$REPO_DIR/src/testing_fitness.py" "Q"$k"_"$i "headless_true" $k_enemy&
	    sleep 0.75;
	done
done

wait;


echo "All $num_instances instances have been started.";

