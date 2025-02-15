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

# Start Server
echo "Starting Xpilots Server"
sleep 1

# switchBase 1 = 100% probability to swap bases on death, + teams disables teams
python3 "$REPO_ROOT/src/Engine/xpilots_mod -map $REPO_ROOT/src/Engine/maps/core.xp -noquit +teamPlay -maxRoundTime 60 -roundsToPlay 0 +limitedLives -maxClientsPerIP 100"

#exit
