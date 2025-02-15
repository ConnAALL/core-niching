#!/bin/bash

# Loop from 1 to 32
for ((i = 1; i <= 32; i++)); do
  (
    # Call the command, replacing "5" with the current iteration number
    ./xpilot -join localhost -name X"$i" &
    sleep 1;
    )
done
