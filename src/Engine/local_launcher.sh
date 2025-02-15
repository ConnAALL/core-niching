#!/usr/bin/bash
# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")

# Loop from 1 to 32
for ((i = 1; i <= 32; i++)); do
  (
    # Call the command, replacing "5" with the current iteration number
    python3 "$SCRIPT_DIR/../core_controller.py" A_$RANDOM&
    sleep 1;
    )
done

#echo "Launched 32 agents on machine, exiting.";
#exit;
