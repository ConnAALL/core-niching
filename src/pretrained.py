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
from datetime import datetime, timezone
import ast

load_dotenv()
DEFAULT_HEADLESS = os.getenv("DEFAULT_HEADLESS") 
SERVER_IP = os.getenv("SERVER_IP")

# Get the directory of the current script
current_dir = os.path.dirname(os.path.realpath(__file__))

# Go back to the root of the repository
repo_root = os.path.abspath(os.path.join(current_dir, ".."))

class CoreAgent(ShipData):
    def __init__(self, bot_name): 

        # Ship/bot data
        ShipData.__init__(self)
        self.bot_name = bot_name

        # Directories
        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.repo_root, 'data')
        os.makedirs(self.data_path, exist_ok=True)
        self.error_log_path = os.path.join(self.repo_root, 'tracebacks')
        os.makedirs(self.error_log_path, exist_ok=True)

        # Chromesome/csv file path
        self.bin_chromosome = self.handle_spawn_chrome() # Generate inital chromosome, make csv file if its not already there
        self.dec_chromosome = Evolver.read_chrome(self.bin_chromosome) # Read chromosome as decimal value
        self.csv_file_path = os.path.join(self.data_path, f'{self.bot_name}.csv')

        # Evolution stuff
        self.initialized = False # Chromosome not yet generated
        self.MUT_RATE = 300
        self.GENES_PER_LOOP = 8
        self.SPAWN_QUAD = None
        self.bot_name = bot_name
        self.current_loop = None
        self.current_loop_idx = 0
        self.current_gene_idx = 0
        self.current_loop_started = False

        # Hardcoded robot capability
        # So for power, I ran the system for around 24 hours at 5 power, 8 power, 10 power and 20 power, it seems like the smaller powers have a better self death to kill ratio, but this is the unmodifed action gene, and I think I ran the lower power systems for longer so they had more a chance to evolve
        # anyway, 5 did the best but 8 followed pretty closely behind, and 8 seems like the minimum power that you need to be to recover when blown off course by another agent exploding, so thats why its 8 for now
        ai.setPower(8.0) # Power 5-55, amount of thrust
        ai.setTurnSpeed(64.0) # Turn speed 5-64

        # Initial score
        self.num_kills = 0
        self.num_self_deaths = 0
        self.score = 0
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
        self.SD = False

        # Misc 
        step = 10
        self.generate_feelers(step) # Generate feelers at every stepth degree from 0-359 degrees

    def increment_gene_idx(self):
        self.current_gene_idx = (self.current_gene_idx + 1) \
                                % self.GENES_PER_LOOP
        return self.current_gene_idx
    
    def update_score(self):
        self.score = ai.selfScore()

    def log_error(self, traceback_str, function_name):
        current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        fs = os.path.join(self.error_log_path, f'{function_name}_error_{self.bot_name}.txt')
        with open(fs, "a") as f:
            f.write(f"Error in {function_name} for agent {self.bot_name} at {current_time}\n")
            f.write(traceback_str)

    def create_csv(self):
        """Create a CSV file in the data directory with the name of the bot."""
        try:
            csv_file_path = os.path.join(self.data_path, f'{self.bot_name}.csv')
            with open(csv_file_path, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Bot Name', 'Spawn Quadrant', 'Kills', 'Self Deaths', 'Score', 'Cause of Death', 'Binary Chromosome', 'Decimal Chromosome'])  # Things we track
            print(f"CSV file created successfully at {csv_file_path}")
            return csv_file_path # Give csv_file_path to use later
        except Exception as e:
            print(f"Failed to create CSV file: {e}")
            self.log_error(traceback.format_exc(), 'create_csv')

    def handle_spawn_chrome(self):
        """
        Handle chromosome initialization when bot spawns.
        Checks for existing CSV with bot's data and loads last chromosome,
        or generates a new chromosome if no data exists.
        """
        csv_path = os.path.join(self.data_path, f'{self.bot_name}.csv')
        
        if not os.path.exists(csv_path):
            print(f"First run for {self.bot_name} - creating new CSV and chromosome")
            self.create_csv()
            #return Evolver.generate_chromosome()
            return (['100001001', '011101010', '011011001', '011100101', '000100011', '000111000', '000100101', '000010111'], ['100010101', '001001001', '011001111', '001000111', '011001110', '001001010', '010110100', '011001001'], ['100101100', '011100110', '010011001', '010001000', '000110111', '010101010', '000000100', '001010010'], ['100111010', '000110111', '010110111', '000011011', '000001011', '001110101', '000110011', '000000111'], ['101000110', '000101101', '000101101', '000100010', '010111100', '001111010', '011101010', '010111111'], ['101010111', '001110100', '001100011', '010010110', '000110001', '011111001', '010001001', '011110010'], ['101101110', '001111011', '001001000', '011110000', '001101101', '011101010', '000011101', '010001010'], ['101111011', '001010010', '000111100', '001111100', '010000111', '011110110', '001010100', '010101000'], ['110000000', '010010100', '000100100', '010000101', '001011000', '010111111', '010011101', '001110100'], ['110010100', '001001011', '001110101', '011001111', '001000101', '000111010', '010011110', '000000100'], ['110101001', '011101001', '001110110', '000101011', '000011001', '010010000', '010101011', '001011100'], ['110110000', '000010101', '010100111', '011111001', '011101111', '010001000', '000111000', '001100000'], ['111000001', '011111101', '001101100', '010111111', '001111001', '010000001', '010011101', '000101000'], ['111010111', '001100000', '010110011', '000111111', '001001110', '010110010', '000000101', '011011110'], ['111101111', '001010101', '001101101', '011101101', '000011010', '010010000', '001001111', '000011101'], ['111111110', '001001110', '010000010', '000011001', '000000100', '010011011', '000110110', '000000001'])

        # Check if CSV exists and has data
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='') as csvfile:
                csv_rows = list(csv.reader(csvfile))
                if len(csv_rows) > 1:  # If we have data rows beyond header
                    last_row = csv_rows[-1]
                    last_chromosome_str = last_row[6]  # Binary chromosome is in column 6
                    try:
                        last_chromosome = ast.literal_eval(last_chromosome_str)
                        print(f"Found existing chromosome for {self.bot_name}")
                        return last_chromosome
                    except (ValueError, SyntaxError):
                        print(f"Could not parse existing chromosome, generating new one")
                        self.bin_chromosome = Evolver.generate_chromosome()

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

    def write_soul_data(self, ftype="a"):
        """Log agent data to CSV.
        
        Parameters:
            ftype: File type 
        """
        try:
            # Determine cause of death
            if "null" in self.last_death:
                cause_of_death = "Wall Collision"  
            else:
                cause_of_death = f"Killed by {self.last_death[0]}" # null if self death
            
            # Prepare data row
            data_row = [
                self.bot_name,          # Bot Name
                self.SPAWN_QUAD,        # Spawn Quadrant
                self.num_kills,         # Kills
                self.num_self_deaths,   # Self Deaths
                self.score,             # Score
                cause_of_death,         # Cause of Death
                self.bin_chromosome,     # Binary Chromosome
                Evolver.read_chrome(self.bin_chromosome)     # Decimal Chromosome
            ]
            
            # Write to CSV file
            with open(self.csv_file_path, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(data_row)
                
            print(f"Data logged to CSV for {self.bot_name}")
            print(f"Score: {self.score}")
            print(f"Chromosome: {self.bin_chromosome}")
                        
        except Exception as e:
            print(f"Failed to write data to CSV: {e}")
            self.log_error(traceback.format_exc(), 'write_soul_data')
    
    def get_kills(self):
        # If we got plus or minus 9 pts, it means we got a kill, minus is fine because team killing counts
        compare_score = abs(self.score - ai.selfScore())
        if compare_score > 9.0:
            self.num_kills += 1
        self.score = ai.selfScore()
        
    def was_killed(self):        
        
        print(f"Last death is {self.last_death}")
        print(f"Current Score: {self.score}")

        
        if "null" in self.last_death:  # If ran into wall, dont crossover
            print(f"Agent {self.bot_name} ran into wall (or self destructed some other way)")
            self.num_self_deaths += 1
            #self.bin_chromosome = Evolver.mutate(self.bin_chromosome, self.MUT_RATE)  # Chance for mutation on self death, turned off for now because original paper doesnt have it

        if ai.selfAlive() == 0 and self.crossover_completed is False:
            killer = self.last_death[0]  # Get killer name
            killer_csv = os.path.join(self.data_path, f'{killer}.csv')  # Construct killer's CSV path
            
            if killer != 'null':
                print(f"{killer} killed {self.bot_name}")
                try:
                    # Read the killer's CSV file to get their latest chromosome
                    with open(killer_csv, 'r', newline='') as csvfile:
                        # Read all rows to get the last one
                        csv_rows = list(csv.reader(csvfile))
                        if len(csv_rows) > 1:  # Make sure we have data rows beyond the header
                            last_row = csv_rows[-1]
                            killer_chromosome_str = last_row[6]  # Binary chromosome is in column 6
                            killer_chromosome = None
                            try:
                                killer_chromosome = ast.literal_eval(killer_chromosome_str)
                            except (ValueError, SyntaxError) as parse_error:
                                print(f"Error parsing chromosome data for killer {killer}: {parse_error}")
                                return
                            if killer_chromosome != None:
                                cross_over_child = Evolver.crossover(self.bin_chromosome, killer_chromosome)
                                self.bin_chromosome = Evolver.mutate(cross_over_child, self.MUT_RATE)
                                self.crossover_completed = True
                        else:   
                            print(f"No chromosome data found for killer {killer}")
                            return
                        
                except Exception as e:
                    print(f"Error processing killer data: {e}")
                    traceback_str = traceback.format_exc()
                    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    fs = os.path.join(self.repo_root, 'tracebacks', f'killer_data_error_{self.bot_name}.txt')
                    with open(fs, "a") as f:
                        f.write(f"Error processing killer {killer} data for agent {self.bot_name} at {current_time}\n")
                        f.write(traceback_str)

                except FileNotFoundError:
                    print(f"Could not find CSV file for killer {killer}")
                    traceback_str = traceback.format_exc()
                    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    fs = os.path.join(self.repo_root, 'tracebacks', f'CSV_NOT_FOUND_{killer}.txt')
                    with open(fs, "a") as f:
                        f.write(f"Could not find CSV file for killer {killer} at {current_time}\n")
                        f.write(traceback_str)
                    # If we can't find the killer's data, just mutate our current chromosome
                    self.bin_chromosome = Evolver.mutate(self.bin_chromosome, self.MUT_RATE)
                    self.write_soul_data()
        
        self.spawn_set = False
        self.write_soul_data()

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
                self.SPAWN_QUAD = 2
            elif spawn_x < 0 and spawn_y >= 0:
                self.SPAWN_QUAD = 1
            elif spawn_x < 0 and spawn_y < 0:
                self.SPAWN_QUAD = 3
            else:
                self.SPAWN_QUAD = 4

        return self.SPAWN_QUAD

def loop():
    global agent
    global bot_name
    
    if agent is None:
        agent = CoreAgent(bot_name)

    try:
        if ai.selfAlive() == 1:
            
            if agent.spawn_set == False: # Agent is spawning in
                agent.update_agent_data()
                agent.SPAWN_QUAD = agent.set_spawn_quad()            
                print(f"Agent {bot_name} spawned in quadrant {agent.SPAWN_QUAD}")
                agent.dec_chromosome = Evolver.read_chrome(agent.bin_chromosome) # Read chromosome as decimal value
                agent.current_loop_started = False
                agent.spawn_set = True
                agent.SD = False

            if agent.movement_timer == -1.0: # Set timer if not set
                agent.movement_timer = time.time()
                agent.SD = False
                #print("Initial SD timer set")

            if agent.agent_data["X"] != ai.selfX() or agent.agent_data["Y"] != ai.selfY(): # If agent is moving update time
                agent.movement_timer = time.time()

            if not agent.SD and time.time() - agent.movement_timer > 10.0: # If agent hasnt moved for 10 seconds, SD to get to a better area, SD is an input so we also get an input to avoid getting kicked
                ai.selfDestruct()
                agent.SD = True
                print("SD'ing")
                # I think I disabled the pause feature but I'm not gonna remove the code until im sure of that

            if agent.bin_chromosome is not None: # If agent has a chromosome, that means its back alive
                
                agent.get_kills() # Update agent kills

                if not agent.current_loop_started:
                    agent.current_loop = agent.dec_chromosome[0]
                    agent.current_loop_started = True

                agent.frames_dead = 0

                agent.update_agent_data()
                agent.update_enemy_data()
                agent.update_bullet_data()
                agent.update_score()

                agent.crossover_completed = False # Reset crossover flag
                gene = agent.current_loop[agent.current_gene_idx]

                if Evolver.is_jump_gene(gene):
                    if agent.check_conditional(gene[1]):
                        agent.current_loop_idx = gene[2]
                        agent.current_loop = \
                            agent.dec_chromosome[agent.current_loop_idx]
                        agent.current_gene_idx = 0
                        return
                    else:
                        agent.increment_gene_idx()

                gene = agent.current_loop[agent.current_gene_idx]
                ActionGene(gene, agent)
                agent.increment_gene_idx()
            else:
                # Error information
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                error_msg = (
                    f"ERROR: Missing Chromosome\n"
                    f"Time: {current_time}\n"
                    f"Bot: {bot_name}\n"
                    f"Quadrant: {agent.SPAWN_QUAD}\n"
                    f"Frames Dead: {agent.frames_dead}\n"
                    f"Crossover Completed: {agent.crossover_completed}\n"
                )
                
                # Get the full traceback
                trace = traceback.format_exc()
                
                # Write to error log
                error_log_path = os.path.join(agent.error_log_path, f'missing_chromosome_error_{current_time}.txt')
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
            agent.movement_timer = -1.0 # For SD
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
        fs = os.path.join(agent.repo_root, 'tracebacks', 'AI_loop_exception_{}.txt'.format(agent.bot_name))
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
        
        if HEADLESS not in answers: # If we did not argue something that sounds like we don't want it to run in headless, run in headless
            ai.headlessMode()
        
        if team != -1:
            ai.start(loop, ["-name", bot_name, "-join", SERVER_IP, "-team", str(team)])
        else:
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

