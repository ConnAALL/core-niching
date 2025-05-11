# core-niching
- Using a unique competitive coevolution method to niche agents in the game Xpilot to quadrants on "the core" map
- Each agent spawns with a unique chromosome that determines their actions, crossover happens when one agent shoots another
- Work up to May 4th 2025 was documented and [presented](https://docs.google.com/presentation/d/1PvMrOg0gD0Rf9me3HLC0duRAI0g9anFMiGSZoE4nqOo/edit?usp=sharing) during the COM 496 research presentations on May 5th 2025

## Requirements
1. Computer made after the year 1995 running some sort of linux distro
2. At least 1 gigabyte of storage per 24 hours of training 

## First time setup
1. pip install -r requirements.txt
2. Unzip compile.zip
3. Navigate to root/compile/scripts/xpilot-ai-1.1.1604-linux.sh and run
4. From there, open xpilot-ai
5. Copy xpilots_mod and navigate to root/src/Engine
6. Paste xpilots_mod over the old xpilots_mod

## To train (niched agents):
1. Navigate to root/utils
2. Run reset_traceback_and_data.sh to clear the data folder, ignore this if you want to continue a previous run
3. Run start_team_server.sh or navigate to root/src/Engine/maps and in the terminal run ./../xpilots_mod -map core_teams.xp -shotKillScoreMult 100 -noquit -teamPlay +switchBase 1.0 -maxRoundTime 60 -roundsToPlay 0 +limitedLives -maxClientsPerIP 120 +teamImmunity
4. Navigate to root/utils/Team Agents and run launch team agents.sh
5. Wait for all agents to finish launching, note that training data is logged in real time to root/data

## To train (non niched agents):
1. Navigate to root/utils
2. Run reset_traceback_and_data.sh to clear the data folder, ignore this if you want to continue a previous run
3. Run start_xpilots_server.sh or navigate to root/src/Engine/maps and in the terminal run ./../xpilots_mod -map core_teams.xp -shotKillScoreMult 100 -noquit +teamPlay +switchBase 1.0 -maxRoundTime 60 -roundsToPlay 0 +limitedLives -maxClientsPerIP 120 +teamImmunity
4. Navigate to root/and run random spawn launcher.sh
5. Wait for all agents to finish launching, note that training data is logged in real time to root/data

## To test our agents fitness (niched agents in their original quadrants vs niched agents from foreign quadrants):
Note that root/testing fitnesses is preloaded with agents that have already been trained for 72 hours, so to run the best agents, we can run the agents already in testing fitnesses
1. Train niched agents or use best agents
2. Cut all data saved in root/data
3. Navigate to root/testing fitnesses
4. Paste
5. Run clean_data.py
6. Navigate to root/utils
7. Run start_battle_server.sh or navigate to root/src/Engine/maps and in the terminal run ./../xpilots_mod -map core_battle.xp -shotKillScoreMult 100 -noquit -teamPlay +switchBase 1.0 -maxRoundTime 60 -roundsToPlay 0 +limitedLives -maxClientsPerIP 120 -teamImmunity
8. Run mix and match battle agents, native.sh and mix and match battle agents, shifted.sh at the same time
9. Let agents battle for at least 6 hours to give the agents a good amount of time to collect results
10. Navigate to root/testing fitnesses
11. Run all cells in compare mix and match.ipynb to get a graph of the agents performance over time, note that by default the graphs go from 0 mins to 864 mins, and 0 kills to 12000 kills, you can adjust that at the top of the last cell

## To test our agents fitness (non niched agents vs niched agents):
Note that root/testing fitnesses is preloaded with agents that have already been trained for 72 hours, so to run the best agents, we can run the agents already in testing fitnesses
1. Train niched agents or use best agents
2. Cut all data saved in root/data
3. Navigate to root/testing fitnesses
4. Paste
5. Navigate to root/utils
6. Train non niched agents or use best agents 
7. Cut all data saved in root/data
8. Navigate to root/testing fitnesses
9. Paste
10. Run clean_data.py
11. Navigate to root/utils
12. Run start_battle_server.sh or navigate to root/src/Engine/maps and in the terminal run ./../xpilots_mod -map core_battle.xp -shotKillScoreMult 100 -noquit -teamPlay +switchBase 1.0 -maxRoundTime 60 -roundsToPlay 0 +limitedLives -maxClientsPerIP 120 -teamImmunity
13. Run battle agents, niched.sh and battle agents, not niched.sh at the same time
14. Let agents battle for at least 6 hours to give the agents a good amount of time to collect results
15. Navigate to root/testing fitnesses
16. Run all cells in compare mix and match.ipynb to get a graph of the agents performance over time, note that by default the graphs go from 0 mins to 864 mins, and 0 kills to 12000 kills, you can adjust that at the top of the last cell


