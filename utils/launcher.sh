#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
# Set the number of instances you want to run
num_instances=60;

# Loop from 1 to num_instances
for ((i = 1; i <= num_instances; i++)); do
    echo "Running instance $i"
    python3 "$SCRIPT_DIR/../src/core_controller.py" $RANDOM "headless_true" &
    sleep 0.75;
    # Note that headless MUST be false if agents have limited lives
done

wait;

echo "All $num_instances instances have been started.";

