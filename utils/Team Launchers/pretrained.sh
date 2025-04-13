#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR=$(dirname "$(dirname "$SCRIPT_DIR")")
# Set the number of instances you want to run
num_agents=32
not_headless=1


# Launch not headless agents 
for ((i = 1; i <= not_headless; i++)); do	
	python3 "$REPO_DIR/src/pretrained.py" "pre_"$i "headless_false" 3&
	sleep 0.75
done
sleep 1
for ((j = not_headless; j <= num_agents; j++)); do	
	python3 "$REPO_DIR/src/pretrained.py" "pre_"$j "headless_true" 3&
	sleep 0.75
done
wait;

echo "All $num_agents instances have been started.";

