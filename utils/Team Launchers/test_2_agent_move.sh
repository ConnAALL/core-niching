#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR=$(dirname "$(dirname "$SCRIPT_DIR")")
# Set the number of instances you want to run

# Assumes you are using a virtual environment located in the repo root/.venv, delete the following 2 lines if you want to use your global python installation,
# or edit them if you want to use a different virtual environment
cd "$REPO_DIR/.venv" || { echo "Failed to change directory to .venv"; exit 1; }
source bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Launch one agent
for ((j = 1; j <= 2; j++)); do	
	python3 "$REPO_DIR/src/pretrained.py" "test_"$j "headless_false" 3 1&
	sleep 1;
done
wait;

echo "All $num_instances instances have been started.";

