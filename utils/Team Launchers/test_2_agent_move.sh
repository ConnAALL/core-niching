#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR=$(dirname "$(dirname "$SCRIPT_DIR")")
# Set the number of instances you want to run


# Launch one agent
for ((j = 1; j <= 2; j++)); do	
	python3 "$REPO_DIR/src/pretrained.py" "test_"$j "headless_false" 3 1&
	sleep 1;
done
wait;

echo "All $num_instances instances have been started.";

