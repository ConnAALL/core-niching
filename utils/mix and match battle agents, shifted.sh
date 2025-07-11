#!/usr/bin/bash

# What we do here is battle agents niched to an enviornment with agents niched to another enviornment

# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR="$(dirname "$SCRIPT_DIR")"
# Set the number of instances you want to run
num_instances_per_team=30;
split=15;

for ((j = 4; j >= 1; j--)); do	
	k=$(( ((j % 4) + 1) + 4 ))

	python3 "$REPO_DIR/src/testing_fitness.py" "Q"$j"_"$num_instances_per_team "headless_false" $k&
	for ((i = split+1; i <= num_instances_per_team -1; i++)); do
	    echo "Running instance $i"
	    python3 "$REPO_DIR/src/testing_fitness.py" "Q"$j"_"$i "headless_true" $k&
	    sleep 1.5;
	done
done

wait;


echo "All $num_instances instances have been started.";
