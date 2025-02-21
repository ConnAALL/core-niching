from Engine import libpyAI as ai
import os
import sys
import traceback
import json
import uuid
import time
from dotenv import load_dotenv
from ShipData import ShipData
from Evolver import Evolver
from ActionGene import ActionGene
import csv 
import random 
from datetime import datetime

load_dotenv()
DEFAULT_HEADLESS = os.getenv("DEFAULT_HEADLESS") 
SERVER_IP = os.getenv("SERVER_IP")

# Get the directory of the current script
current_dir = os.path.dirname(os.path.realpath(__file__))

# Go back to the root of the repository
repo_root = os.path.abspath(os.path.join(current_dir, ".."))

class CoreAgent(ShipData):
    def __init__(self, bot_name): 
        ShipData.__init__(self)
        self.bot_name = bot_name

        # Directories
        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.repo_root, 'data')
        os.makedirs(self.data_path, exist_ok=True)
        self.error_log_path = os.path.join(self.repo_root, 'tracebacks')
        os.makedirs(self.error_log_path, exist_ok=True)
        self.csv_file_path = self.create_csv() # Generate csv for logging and as a chromosome refrence and save the path

        # Evolution stuff
        self.initialized = False # Chromosome not yet generated
        self.MUT_RATE = 300
        self.GENES_PER_LOOP = 8
        self.chrom_name = ""
        self.SPAWN_QUAD = None
        self.bot_name = bot_name
        self.bin_chromosome = Evolver.generate_chromosome() # Generate inital chromosome
        self.dec_chromosome = Evolver.read_chrome(self.bin_chromosome) # Read chromosome as decimal value

        # Hardcoded robot capability
        ai.setPower(8.0) # Power 5-55, amount of thrust
        # Trying 5 instead of 8 for now
        ai.setTurnSpeed(30.0) # Turn speed 5-64

        # Initial score
        self.num_kills = 0
        self.num_self_deaths = 0
        self.spawn_score = 0
        self.score = 0
        self.SD = False
        self.movement_timer = -1.0
        self.chromosome_iteration = 0

        # Death stuff
        self.framesPostDeath = 0
        self.feed_history = ['' * 5]
        self.last_death = ["null", "null"]
        self.last_kill = ["null", "null"]
        self.prior_death = ["null", "null"]
        self.crossover_completed = False
        self.frames_dead = 0
        self.spawn_set = False
        
        self.generate_feelers(10)

    def create_csv(self):
        """Create a CSV file in the data directory with the name of the bot."""
        try:
            csv_file_path = os.path.join(self.data_path, f'{self.bot_name}.csv')
            with open(csv_file_path, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Bot Name', 'Spawn Quadrant', 'Kills', 'Self Deaths', 'Cause of Death', 'Binary Chromosome', 'Decimal Chromosome'])  # Things we track
            print(f"CSV file created successfully at {csv_file_path}")
            return csv_file_path # Give csv_file_path to use later
        except Exception as e:
            print(f"Failed to create CSV file: {e}")
            self.log_error(traceback.format_exc(), 'create_csv')

    def update_score(self):
        self.score = ai.selfScore()

    def process_server_feed(self):
        self.feed_history = []
        for i in range(5):
            server_message = ai.scanGameMsg(i)
            if self.bot_name in server_message \
                    and "ratio" not in server_message \
                    and "crashed" not in server_message \
                    and "entered" not in server_message \
                    and "suicide" not in server_message \
                    and "How strange!" not in server_message:
                self.feed_history.append(server_message)

        killer = "null"
        victim = "null"
        for message in self.feed_history:
            if "killed" in message:
                victim = message.split(" was")[0]
                killer = message.split("from ")[-1][:-1]
                break
            elif "smashed" in message or "trashed" in message:
                self.last_death = [killer, victim]
                return
        output = [killer, victim]
        if killer == self.bot_name:
            self.last_kill = output
        elif victim == self.bot_name:
            self.last_death = output

    def log_chat_message(self, message): # Log each system message, will probs delete later testing something
        try:
            log_dir = os.path.join(self.repo_root, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file_path = os.path.join(log_dir, f'chat_log_{self.chrom_name}.txt')
            with open(log_file_path, 'a') as log_file:
                log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                log_file.write(f"{log_time} - {message}\n")
        except Exception as e:
            print(f"Failed to log chat message: {e}")
            print(traceback.format_exc())

    def write_soul_data(self, ftype="a", score=0.0):
        """Log agent data to CSV.
        
        Parameters:
            quadrant: The spawn quadrant of the agent
            ftype: File type (kept for backwards compatibility)
            score: The score achieved in this life
        """
        try:
            # Determine cause of death
            cause_of_death = "Wall Collision" if "null" in self.last_death else f"Killed by {self.last_death[0]}" # null if self death
            
            # Prepare data row
            data_row = [
                self.bot_name,          # Bot Name
                self.SPAWN_QUAD,        # Spawn Quadrant
                self.num_kills,         # Kills
                self.num_self_deaths,   # Self Deaths
                cause_of_death,         # Cause of Death
                self.bin_chromosome,     # Binary Chromosome
                Evolver.read_chrome(self.bin_chromosome)     # Decimal Chromosome
            ]
            
            # Write to CSV file
            with open(self.csv_file_path, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(data_row)
                
            print(f"Data logged to CSV for {self.bot_name}")
            print(f"Score: {score}")
            print(f"Chromosome: {self.bin_chromosome}")
            
            # Update local score
            self.spawn_score = self.score
            
        except Exception as e:
            print(f"Failed to write data to CSV: {e}")
            self.log_error(traceback.format_exc(), 'write_soul_data')

    def was_killed(self):        
        agent.update_score()

        print(f"Last death is {self.last_death}")
        print(f"Current Score: {self.score}")
        print(f"Spawn Score: {self.spawn_score}")

        life_score = self.score - self.spawn_score
        print(f"Score to log: {life_score}")
        
        if "null" in self.last_death:  # If ran into wall, dont crossover, just mutate
            print(f"Agent {self.bot_name} ran into wall (or self destructed some other way)")
            self.num_self_deaths += 1
            self.bin_chromosome = Evolver.mutate(self.bin_chromosome, self.MUT_RATE)  # Chance for mutation on self death
            self.write_soul_data(score=life_score)
            self.spawn_set = False
            return

        if ai.selfAlive() == 0 and self.crossover_completed is False:
            killer = self.last_death[0]  # Get killer name
            killer_csv = os.path.join(self.data_path, f'CA_{killer}.csv')  # Construct killer's CSV path
            
            print(f"{killer} killed {self.chrom_name}")

            try:
                # Read the killer's CSV file to get their latest chromosome
                with open(killer_csv, 'r', newline='') as csvfile:
                    # Read all rows to get the last one
                    csv_rows = list(csv.reader(csvfile))
                    if len(csv_rows) > 1:  # Make sure we have data rows beyond the header
                        last_row = csv_rows[-1]
                        new_chromosome = last_row[5]  # Binary chromosome is in column 5
                    else:
                        print(f"No chromosome data found for killer {killer}")
                        return

                # If we got here, we have the killer's chromosome
                cross_over_child = Evolver.crossover(
                    self.bin_chromosome, new_chromosome)
                
                self.bin_chromosome = Evolver.mutate(cross_over_child, self.MUT_RATE)
                
                # Log the result of crossover and mutation
                self.write_soul_data(score=life_score)

                # Reset state
                self.spawn_set = False
                self.crossover_completed = True

            except FileNotFoundError:
                print(f"Could not find CSV file for killer {killer}")
                # If we can't find the killer's data, just mutate our current chromosome
                mutated_child = Evolver.mutate(self.bin_chromosome, self.MUT_RATE)
                self.write_soul_data(score=life_score)
                self.spawn_set = False
                
            except Exception as e:
                print(f"Error processing killer data: {e}")
                traceback_str = traceback.format_exc()
                fs = os.path.join(self.repo_root, 'tracebacks', f'killer_data_error_{self.chrom_name}.txt')
                with open(fs, "a") as f:
                    f.write(f"Error processing killer {killer} data for agent {self.bot_name}\n")
                    f.write(traceback_str)

    def find_min_wall_angle(self, wall_feelers):
        min_wall = min(wall_feelers)
        min_index = wall_feelers.index(min_wall)
        angle = int(10 * min_index)
        return angle if angle < 180 else angle - 360

    def find_max_wall_angle(self, wall_feelers):
        max_wall = max(wall_feelers)
        max_index = wall_feelers.index(max_wall)
        angle = int(10 * max_index)
        return angle if angle < 180 else angle - 360

    def check_conditional(self, conditional_index):
        min_wall_dist = min(self.agent_data["head_feelers"])
        conditional_list = [self.agent_data["speed"] < 6, self.agent_data["speed"] > 10,
                            self.enemy_data["distance"] < 50, self.agent_data["head_feelers"][0] < 100,
                            self.enemy_data["distance"] < 200 and self.enemy_data["direction"] == 1,
                            self.enemy_data["distance"] < 150 and self.enemy_data["direction"] == 2,
                            self.enemy_data["distance"] < 100 and self.enemy_data["direction"] == 3,
                            self.enemy_data["distance"] < 100 and self.enemy_data["direction"] == 4,
                            min_wall_dist < 75, min_wall_dist < 200, min_wall_dist > 300,
                            self.bullet_data["distance"] < 100, self.bullet_data["distance"] < 200,
                            self.bullet_data["distance"] < 50, self.enemy_data["distance"] == -1,
                            self.agent_data["speed"] == 0]
        return conditional_list[conditional_index]

    def set_spawn_quad(self):
        print("X: {}".format(self.agent_data["X"]))
        print("Y: {}".format(self.agent_data["Y"]))

        if self.agent_data["X"] != -1:
            spawn_x = self.agent_data["X"] - 4500
            spawn_y = self.agent_data["Y"] - 4500

            if spawn_x >= 0 and spawn_y >= 0:
                agent.SPAWN_QUAD = 1
            elif spawn_x < 0 and spawn_y >= 0:
                agent.SPAWN_QUAD = 2
            elif spawn_x < 0 and spawn_y < 0:
                agent.SPAWN_QUAD = 3
            else:
                agent.SPAWN_QUAD = 4

        return agent.SPAWN_QUAD

def loop():
    global agent
    global bot_name
    global team 

    if team != -1:
        message = (f"/team {team}")
        ai.talk(message)
        print(f"Agent {bot_name} joined team {team}.")
        team = -1
    
    if agent is None:
        agent = CoreAgent(bot_name)

    try:
        if ai.selfAlive() == 1:
            if agent.spawn_set == False: # Agent is spawning in
                spawn = agent.set_spawn_quad()            
                print(f"Agent {bot_name} spawned in quadrant {spawn}")
                agent.spawn_score = ai.selfScore()
                agent.dec_chromosome = Evolver.read_chrome(agent.bin_chromosome) # Read chromosome as decimal value
                agent.SD = False
                agent.spawn_set = True

            #SD is a leftover from Aarons code, idk if I will keep it or not

            #if agent.movement_timer == -1.0: # Set timer if not set
            #    agent.movement_timer = time.time()
            #    agent.SD = False
            #    print("Initial SD timer set")

            #if agent.agent_data["X"] != ai.selfX() or agent.agent_data["Y"] != ai.selfY(): # If agent is moving update time
            #    agent.movement_timer = time.time()

            #if time.time() - agent.movement_timer > 5.0 and not agent.SD: # If agent hasnt moved for 5 seconds, SD
            #    ai.selfDestruct()
            #    agent.SD = True
            #    print("SD'ing")

            if agent.bin_chromosome is not None: # If agent has a chromosome, that means its back alive
                agent.frames_dead = 0

                agent.update_agent_data()
                agent.update_enemy_data()
                agent.update_bullet_data()
                agent.update_score()

                agent.crossover_completed = False # Reset crossover flag

                ActionGene(agent.dec_chromosome, agent)
            else:
                # Generate detailed error information
                error_time = datetime.utcnow().strftime('%Y-%M-%D_%H-%M-%S')
                error_msg = (
                    f"ERROR: Missing Chromosome\n"
                    f"Time: {error_time}\n"
                    f"Bot: {bot_name}\n"
                    f"Quadrant: {agent.SPAWN_QUAD}\n"
                    f"Score: {agent.spawn_score}\n"
                    f"Frames Dead: {agent.frames_dead}\n"
                    f"Crossover Completed: {agent.crossover_completed}\n"
                )
                
                # Get the full traceback
                trace = traceback.format_exc()
                
                # Write to error log
                error_log_path = os.path.join(agent.error_log_path, f'missing_chromosome_error_{error_time}.txt')
                with open(error_log_path, 'w') as f:
                    f.write(error_msg)
                    f.write("\nTraceback:\n")
                    f.write(trace)
                    f.write("\nGenerating new chromosome as fallback...\n")
                
                print(error_msg)
                print(f"Full error log written to: {error_log_path}")
                
                # Generate new chromosome as fallback
                agent.bin_chromosome = Evolver.generate_chromosome()
                
        else: # You died :(
            agent.process_server_feed()
            agent.frames_dead += 1
            agent.agent_data["X"] = -1
            agent.agent_data["Y"] = -1
            if agent.frames_dead >= 5: 
                agent.was_killed()
                agent.frames_dead = sys.maxsize * -1 # Agent is dead, so do not crossover until otherwise

    except Exception as e:
        print("Exception in AI Loop")
        print(str(e))
        traceback.print_exc()
        traceback_str = traceback.format_exc()
        fs = os.path.join(agent.repo_root, 'tracebacks', 'AI_loop_exception_{}.txt'.format(agent.chrom_name))
        with open(fs, "w") as f:
            f.write(traceback_str)
            f.write(str(agent.bin_chromosome))
            f.write(str(agent.dec_chromosome))
        ai.quitAI()

def main():
    try:
        global bot_name
        bot_name = "CA_{}".format(sys.argv[1])
        global agent
        agent = None
        HEADLESS = ""

        answers = ["f", "false", "0", "n", "no", "headless_false", "head_false"] # Answers that let you turn headless off
        if len(sys.argv) > 2: # If we specified we want to run in headless mode or not 
            ans = sys.argv[2].lower() # Make answer consistent
            HEADLESS = ans
        else: # Otherwise rely on env default
            HEADLESS = DEFAULT_HEADLESS
        
        global team
        if len(sys.argv) > 3:
            team = int(sys.argv[3]) # Enter team
        else:
            team = -1
        
        print(team)

        if HEADLESS not in answers: # If we did not argue something that sounds like we don't want it to run in headless, run in headless
            ai.headlessMode()
        
        ai.start(loop, ["-name", bot_name, "-join", SERVER_IP])

    except Exception as e:
        print("Exception in main")
        print(str(e))
        traceback.print_exc()

        traceback_str = traceback.format_exc()

        # Write the traceback to file
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        traceback_dir = os.path.join(repo_root, "tracebacks")

        # Ensure the traceback directory exists
        os.makedirs(traceback_dir, exist_ok=True)

        # Construct the traceback file path
        traceback_file_path = os.path.join(traceback_dir, "traceback_main_{}.txt".format(bot_name))

        with open(traceback_file_path, "w") as file:
            file.write(traceback_str)
        
        sys.exit(1)

if __name__ == "__main__":
    main()

