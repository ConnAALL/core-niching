#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_ROOT=$(dirname "$SCRIPT_DIR")

# Reset all at start of new run

rm -r "$REPO_ROOT/data"
rm -r "$REPO_ROOT/tracebacks"
rm -r "$REPO_ROOT/logs"

mkdir "$REPO_ROOT/data"
mkdir "$REPO_ROOT/tracebacks"
mkdir "$REPO_ROOT/logs"

echo "Wiped data & traceback folder"
sleep 3

#exit
