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
        #self.interface = AgentInterface(bot_name)
        
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
        self.LOOPS_PER_CHROME = 12
        self.SPAWN_QUAD = None # Spawn quad isnt really all that important anymore, but its still cool to have so why not just keep it
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
        self.time_born = -1.0 # Time born, for age of adolescence and regeneration pause
        self.age_of_adolescence = 3 # This many seconds old to spread genes as a killer
        self.regeneration_pause = False # Should I pause on self death? (Should start as False)
        self.pause_penalty = 0 # Pause for this many seconds after a self death

        # Misc 
        self.generate_feelers() # Generate initial feelers
        self.debug = debug # Set to true if we want to print out a bunch of info about the agent while its running

    def increment_gene_idx(self):
        reset = True if self.GENES_PER_LOOP == self.current_gene_idx + 1 else False # Return true if we looped around
        self.current_gene_idx = (self.current_gene_idx + 1) % self.GENES_PER_LOOP
        return reset
    
    def increment_loop_idx(self):
        self.current_loop_idx = (self.current_loop_idx + 1) % self.LOOPS_PER_CHROME
        return self.current_loop_idx
    
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
                csv_writer.writerow(['Kills', 'Self Deaths', 'Cause of Death', 'Binary Chromosome', 'Time Born'])  # Things we track
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
            return Evolver.generate_chromosome()

        # Check if CSV exists and has data
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='') as csvfile:
                csv_rows = list(csv.reader(csvfile))
                if len(csv_rows) > 1:  # If we have data rows beyond header
                    last_row = csv_rows[-1]
                    last_chromosome_str = last_row[3]  # Binary chromosome is in column 4
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
                self.num_kills,         # Kills
                self.num_self_deaths,   # Self Deaths
                cause_of_death,         # Cause of Death
                self.bin_chromosome,     # Binary Chromosome
                self.time_born           # Time Born
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
        # If we got plus or minus 100 pts, it means we got a kill, minus is fine because team killing counts
        compare_score = abs(self.score - ai.selfScore())
        if compare_score > 100.0:
            if ai.selfAlive() == 1: # Only way to get + or - 100 pts while not dying is getting a kill
                self.num_kills += 1
        self.score = ai.selfScore()
        
    def was_killed(self):        
        
        print(f"Last death is {self.last_death}")
        print(f"Current Score: {self.score}")

        if "null" in self.last_death:  # If ran into wall, dont crossover, just mutate
            print(f"Agent {self.bot_name} ran into wall (or self destructed some other way)")
            self.num_self_deaths += 1
            agent.regeneration_pause = True # Regeneration pause penalty if self death

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
                            killer_chromosome_str = last_row[3]  # Binary chromosome is in column 4
                            killer_chromosome = None
                            killer_time_of_birth = float(last_row[4])
                            try:
                                killer_chromosome = ast.literal_eval(killer_chromosome_str)
                            except (ValueError, SyntaxError) as parse_error:
                                print(f"Error parsing chromosome data for killer {killer}: {parse_error}")
                                return
                            if killer_chromosome != None and time.time() - killer_time_of_birth > self.age_of_adolescence:
                                if self.debug: 
                                    print("Agent killed by adult, crossing over")
                                cross_over_child = Evolver.crossover(self.bin_chromosome, killer_chromosome)
                                self.bin_chromosome = Evolver.mutate(cross_over_child, self.MUT_RATE)
                                self.crossover_completed = True
                            elif self.debug:
                                print("Agent killed by child, no crossover")
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
        
        self.spawn_set = False

    def find_min_wall_angle(self, wall_feelers):
        # Pick the (distance, angle) tuple with the smallest distance
        dist, angle = min(wall_feelers, key=lambda w: w[0])
        return angle if angle < 180 else angle - 360

    def find_max_wall_angle(self, wall_feelers):
        # Pick the (distance, angle) tuple with the largest distance
        dist, angle = max(wall_feelers, key=lambda w: w[0])
        return angle if angle < 180 else angle - 360
    
    def find_direction_diff(self):
        raw_diff = ai.selfTrackingDeg() - ai.selfHeadingDeg()
        # Wrap into [-180, +180]
        wrapped = (raw_diff + 180) % 360 - 180
        return abs(wrapped)

    def check_conditionals(self):
        """
        Evaluates environmental conditions based on a conditional index value.
        
        Literally a production system of sorts that jumps to a certain gene in 
        the chromosome to handle behaviors if certain conditions are met. 
        
        The conditions cover a variety of game state situations:
        - Ship speed ranges (too slow, too fast)
        - Enemy proximity and direction quadrant
        - Wall distances (collision avoidance)
        - Bullet proximity (evasion)
        - Absence of enemies or movement
        
        Returns:
            Conditional index of most important conditional satisfied
        """

        # Get the minimum distance to a wall from all feelers
        head_feeler_values = [wall[0] for wall in self.agent_data["head_feelers"]]
        track_feeler_values = [wall[0] for wall in self.agent_data["track_feelers"]]
        min_wall_dist_heading = min(head_feeler_values)
        min_wall_dist_tracking = min(track_feeler_values)
        direction_diff = abs(self.find_direction_diff())

        if self.debug:
            print(f"Heading {ai.selfHeadingDeg()}, Tracking {ai.selfTrackingDeg()}, Diff {direction_diff}")
            print(f"Closest wall (heading) is {min_wall_dist_heading} away")
            print(f"Closest wall (tracking) is {min_wall_dist_tracking} away")
            print(f"Closest bullet is {self.bullet_data['distance']} away")
            print(f"Closest enemy is {self.enemy_data['distance']} away")
            print(f"Speed is {self.agent_data['speed']}")

        # List of all possible conditions that can be checked
        conditional_list = [
            # Special conditions
            self.enemy_data["distance"] == -1,             # 0: No enemy detected
            self.agent_data["speed"] == 0,                  # 1: Ship is not moving
            
            # Enemy-based conditions 1
            self.enemy_data["distance"] < 200 and self.enemy_data["distance"] > 100,             # 2: Enemy far but still visable (< 200 units)

            # Wall distance thresholds 1
            min_wall_dist_heading < 200 and min_wall_dist_heading > 100,                           # 3: Wall sort of close (< 200 units)

            # Bullet distance thresholds 1
            self.bullet_data["distance"] < 150 and self.bullet_data["distance"] > 75,             # 4: Bullet sort of close (< 150 units)

            # Speed-based conditions
            self.agent_data["speed"] < 5,                  # 5: Speed too low (< 5)
            self.agent_data["speed"] > 12,                 # 6: Speed too high (> 12)

            # Difference in tracking and heading thresholds 
            direction_diff > 100,                          # 7: Ship is very off course (< 100 degrees)
            direction_diff > 30 and direction_diff < 100,                           # 8: Ship is a bit off course (< 30 degrees)

            # Enemy-based conditions 2
            self.enemy_data["distance"] < 100 and self.enemy_data["distance"] > -1,             # 9: Enemy within firing distance (< 100 units)

            # Wall distance thresholds 2
            min_wall_dist_heading < 100 and min_wall_dist_heading > -1,                            # 10: Wall very close (< 100 units)

            # Bullet distance thresholds 2
            self.bullet_data["distance"] < 80 and self.bullet_data["distance"] > -1           # 11: Bullet very close (< 80 units)

            ]

        conds = [i for i, condition in enumerate(conditional_list) if condition] # List of all true conditionals

        closest_thing = {}
        if 2 in conds:
            closest_thing[2] = self.enemy_data["distance"]
        if 3 in conds:
            closest_thing[3] = min_wall_dist_heading
        if 4 in conds:
            closest_thing[4] = self.bullet_data["distance"]

        if closest_thing: # Purge non closest things
            chosen_index = min(closest_thing, key=closest_thing.get)
            for idx in list(closest_thing.keys()):
                if idx != chosen_index and idx in conds:
                    conds.remove(idx)

        closest_thing = {}
        if 9 in conds:
            closest_thing[9] = self.enemy_data["distance"]
        if 10 in conds:
            closest_thing[10] = min_wall_dist_heading
        if 11 in conds:
            closest_thing[11] = self.bullet_data["distance"]

        if closest_thing: # Purge non closest things
            chosen_index = min(closest_thing, key=closest_thing.get)
            for idx in list(closest_thing.keys()):
                if idx != chosen_index and idx in conds:
                    conds.remove(idx)

        if len(conds) == 0: # If nothing satisfied, return -1
            return -1
        else:
            return max(conds) # Return the highest prority conditional

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
            
            #if agent.debug:
            #    print(agent.dec_chromosome)

            if agent.spawn_set == False: # Agent is spawning in
                agent.time_born = time.time() # For age of adolescence and regeneration pause
                agent.write_soul_data()
                agent.update_agent_data()
                agent.SPAWN_QUAD = agent.set_spawn_quad()            
                print(f"Agent {bot_name} spawned in quadrant {agent.SPAWN_QUAD}")
                agent.dec_chromosome = Evolver.read_chrome(agent.bin_chromosome) # Read chromosome as decimal value
                agent.current_loop_started = False
                agent.spawn_set = True
                agent.SD = False

            if agent.movement_timer == -1.0: # Set timer if not set, don't start until regeneration pause is done
                agent.movement_timer = time.time()
                agent.SD = False
                #print("Initial SD timer set")

            if agent.agent_data["X"] != ai.selfX() or agent.agent_data["Y"] != ai.selfY(): # If agent is moving update time
                agent.movement_timer = time.time()

            if not agent.SD and time.time() - agent.movement_timer > 10.0 + agent.pause_penalty: # If agent hasnt moved for 10 seconds, SD to get to a better area, SD is an input so we also get an input to avoid getting kicked, factor pause penalty into account, if pause penalty is something insane (like over 5), higher chance of getting kicked
                ai.selfDestruct()
                agent.SD = True
                print("SD'ing")

            if agent.regeneration_pause and abs(time.time() - agent.time_born) >= agent.pause_penalty: # If pause penalty is up, we are good
                agent.regeneration_pause = False 
                #print("Regen Penalty Over")
            
            if agent.regeneration_pause: # We gotta wait for the pause penalty to be done
                return
            elif agent.bin_chromosome is not None: # If agent has a chromosome, that means its back alive, main loop, we wait for regeneration pause to be over

                agent.get_kills() # Update agent kills count

                # Initialize the first loop if not already started
                if not agent.current_loop_started:
                    agent.current_loop = agent.dec_chromosome[1]  # Start with the no speed condition because thats accurate to where you will start
                    agent.current_loop_started = True
                    ai.thrust(1)
                
                agent.frames_dead = 0  # Reset frames dead counter since agent is alive
                
                # Update all sensor data from the environment
                agent.update_agent_data()    # Update positional data, speed, heading
                agent.update_enemy_data()    # Update enemy detection and tracking
                agent.update_bullet_data()   # Update bullet detection and tracking
                agent.update_score()         # Update current score from game
                
                agent.crossover_completed = False  # Reset the crossover flag for next death event
                
                # Get the current gene to execute from the current loop
                gene = agent.current_loop[agent.current_gene_idx]
                if agent.debug:
                    print(f"At gene {agent.current_loop_idx}.")
                # Process jump genes (control flow instructions)
                if Evolver.is_jump_gene(gene): # If we have reached a jump gene
                    jump_to = agent.check_conditionals() # Find highest prority conditional
                    if jump_to != -1: 
                        agent.current_loop_idx = jump_to # Jump to highest prority conditional
                        if agent.debug:
                                print(f"Jumped to gene {agent.current_loop_idx}.")
                        agent.current_loop = agent.dec_chromosome[agent.current_loop_idx]  # Get the loop from the decoded chromosome
                        agent.current_gene_idx = 0  # Start executing from the first gene in the new loop
                    else: # If no conditionals satisfied, move on to next loop
                        agent.increment_loop_idx()
                        agent.current_loop = agent.dec_chromosome[agent.current_loop_idx]  # Get the loop from the decoded chromosome
                    agent.increment_gene_idx() # Get out of jump gene territory
                    return # Done with jump eval

                # Now we have found our conditional
                # Process action genes (ship control instructions)
                # Get the current gene again (could be different if we've moved to the next one after a jump)
                gene = agent.current_loop[agent.current_gene_idx]
                
                # Execute an ActionGene to control the ship based on the gene data
                ActionGene(gene, agent)
                
                # Move to the next gene for the next execution cycle
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
            ai.thrust(0) # Make sure the thrust key is turned off
            agent.process_server_feed()
            agent.movement_timer = -1.0 # For SD
            agent.frames_dead += 1
            agent.agent_data["X"] = -1
            agent.agent_data["Y"] = -1
            agent.time_born = -1.0

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
            f.write(str(agent.current_loop_idx))
        ai.quitAI()

def main():
    try:
        global bot_name
        bot_name = "CA_{}".format(sys.argv[1])
        global agent
        agent = None
        HEADLESS = ""
        global debug
        debug = False

        head_answers = ["f", "false", "0", "n", "no", "headless_false", "head_false"] # Answers that let you turn headless off
        debug_answers = ["t", "true", "1", "y", "yes", "debug_true"]

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
        
        if len(sys.argv) > 4 and (sys.argv[4].lower()) in debug_answers: # If we want to launch in debug mode
            debug = True

        if HEADLESS not in head_answers: # If we did not argue something that sounds like we don't want it to run in headless, run in headless
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
