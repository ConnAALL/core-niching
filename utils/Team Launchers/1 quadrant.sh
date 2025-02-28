#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR=$(dirname "$(dirname "$SCRIPT_DIR")")
# Set the number of instances you want to run
num_instances_per_team=30;

# Loop from 1 to num_instances_per_team-1
for ((j = 1; j <= 1; j++)); do	
	for ((i = 1; i <= num_instances_per_team-1; i++)); do
	    echo "Running instance $i"
	    python3 "$REPO_DIR/src/core_controller.py" "Q"$j"_"$i "headless_true" $j&
	    sleep 0.75;
	    # Note that headless MUST be false if agents have limited lives
	done
	    # 1 more, not headless so we can see whats going on
	    python3 "$REPO_DIR/src/core_controller.py" "Q"$j"_"$num_instances_per_team "headless_false" $j&
done
wait;

echo "All $num_instances instances have been started.";

