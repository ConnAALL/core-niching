#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR=$(dirname "$0")
REPO_ROOT=$(dirname "$SCRIPT_DIR")

# Start Server
echo "Starting Xpilots Server"
sleep 1

# + = disable, - = enable, https://code.google.com/archive/p/xpilot-ai/wikis/Options.wiki for options
$REPO_ROOT/src/Engine/xpilots_mod -map $REPO_ROOT/src/Engine/maps/core_battle.xp -shotKillScoreMult 100 -noquit -teamPlay -maxRoundTime 60 -roundsToPlay 0 +limitedLives -maxClientsPerIP 120 -teamImmunity +switchBase 1.0 
wait;

