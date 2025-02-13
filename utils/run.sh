#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_ROOT=$(dirname "$SCRIPT_DIR")

rm -r "$REPO_ROOT/data"
rm -r "$REPO_ROOT/tracebacks"
rm -r "$REPO_ROOT/logs"

mkdir "$REPO_ROOT/data"
mkdir "$REPO_ROOT/tracebacks"
mkdir "$REPO_ROOT/logs"

echo "Wiped data & traceback folder"

echo "Launching Queue Server"
ssh slurm01 "python3 $REPO_ROOT/src/QueueServer/queue_server.py > /dev/null 2>&1  &"  > /dev/null 2>&1  &
sleep 3

# Start Server
echo "Starting Xpilots Server"
# switchBase 1 = 100% probability to swap bases on death, + teams disables teams
ssh slurm01 "$REPO_ROOT/src/Engine/xpilots_mod -map $REPO_ROOT/src/Engine/maps/core.xp -noquit -switchBase 1.0 +teamPlay -maxRoundTime 60 -roundsToPlay 0 +limitedLives -maxClientsPerIP 100 > /dev/null 2>&1 &"  > /dev/null 2>&1  &

exit