#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_DIR=$(dirname "$(dirname "$SCRIPT_DIR")")
# Set the number of instances you want to run
num_instances=4;

# Loop from 1 to num_instances
for ((i = 1; i <= num_instances; i++)); do
    echo "Running instance $i"
    python3 "$REPO_DIR/src/core_controller.py" "Q4_"$i "headless_true" "4"&
    sleep 0.75;
    # Note that headless MUST be false if agents have limited lives
done

# 1 more, not headless so we can see whats going on
for ((i = num_instances; i <= num_instances+1; i++)); do
    echo "Running instance $i"
    python3 "$REPO_DIR/src/core_controller.py" "Q4_"$i "headless_false" "4"&
    sleep 0.75;
    # Note that headless MUST be false if agents have limited lives
done

wait;

echo "All $num_instances instances have been started.";

