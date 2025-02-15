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
python3 "$REPO_ROOT/src/QueueServer/queue_server.py"
sleep 3

#exit
