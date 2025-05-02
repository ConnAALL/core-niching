#!/usr/bin/bash
# Get the directory of the current script
# Set the number of instances you want to run
headless_bots=5;
#head_bots=2;

#for ((i = 1; i <= head_bots; i++)); do
#    echo "Running instance $i"
#    python3 "Expert.py" $i "f"&
#    sleep 1;
#done

python3 "Expert.py" 1 "f"&
for ((i = 2; i <= headless_bots+1; i++)); do
    echo "Running instance $i"
    python3 "Expert.py" $i "t"&
    sleep 1;
done

wait;

echo "All $bots instances have been started.";

