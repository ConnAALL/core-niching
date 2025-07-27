#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR="$(dirname "$SCRIPT_DIR")"
# Set the number of instances you want to run
num_instances_per_team=15;

# Assumes you are using a virtual environment located in the repo root/.venv, delete the following 2 lines if you want to use your global python installation,
# or edit them if you want to use a different virtual environment
cd "$REPO_DIR/.venv" || { echo "Failed to change directory to .venv"; exit 1; }
source bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Loop from 1 to num_instances_per_team-1
for ((j = 5; j <= 8; j++)); do	
	# 1 not headless so we can see whats going on
	python3 "$REPO_DIR/src/testing_fitness.py" "Q"$j"_"$num_instances_per_team "headless_false" $j&
	for ((i = 1; i <= num_instances_per_team-1; i++)); do
	    echo "Running instance $i"
	    python3 "$REPO_DIR/src/testing_fitness.py" "Q"$j"_"$i "headless_true" $j&
	    sleep 1.5;
	    # Note that headless MUST be false if agents have limited lives
	done
done
wait;

echo "All $num_instances instances have been started.";

