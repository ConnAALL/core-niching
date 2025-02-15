#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_ROOT=$(dirname "$SCRIPT_DIR")

rm -r "$REPO_ROOT/data"
rm -r "$REPO_ROOT/tracebacks"

mkdir "$REPO_ROOT/data"
mkdir "$REPO_ROOT/tracebacks"

echo "Purged data folder"
echo "Purged traceback folder"

echo "Launching Queue Server"
python3 "$REPO_ROOT/src/QueueServer/queue_server.py" > queue_server.log &
sleep 3

# Start Server
echo "Starting Xpilots Server"
# switchBase 1 = 100% probability to swap bases on death, + teams disables teams
"$REPO_ROOT/src/Engine/xpilots" -map "$REPO_ROOT/src/Engine/maps/core.xp" -noquit -switchBase 1.0 +teamPlay -maxRoundTime 60 -roundsToPlay 0 -limitedLives -maxClientsPerIP 32 > /dev/null 2>&1 &

# Slurms: 1,3,4,7,8,10,11,12,14,17
# server on slurm01
echo "Starting Agent 1-2"
python3 "$REPO_ROOT/src/core_controller.py" $RANDOM &
python3 "$REPO_ROOT/src/core_controller.py" $RANDOM &
python3 "$REPO_ROOT/src/core_controller.py" $RANDOM &
python3 "$REPO_ROOT/src/core_controller.py" $RANDOM &

echo "Launched agents, exiting."
exit
