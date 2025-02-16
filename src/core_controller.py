from Engine import libpyAI as ai
import os
import sys
import traceback
import json
import uuid
import time
from dotenv import load_dotenv
from NetworkInterface import NetworkInterface
from ShipData import ShipData
from Evolver import Evolver
from ActionGene import ActionGene

load_dotenv()
DEFAULT_HEADLESS = os.getenv("DEFAULT_HEADLESS") 
SERVER_IP = os.getenv("SERVER_IP")

# Get the directory of the current script
current_dir = os.path.dirname(os.path.realpath(__file__))

# Go back to the root of the repository
repo_root = os.path.abspath(os.path.join(current_dir, ".."))

class CoreAgent(NetworkInterface, ShipData):
    def __init__(self, bot_name):
        NetworkInterface.__init__(self)
        ShipData.__init__(self)
        self.initialized = False

        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.MUT_RATE = 300
        self.GENES_PER_LOOP = 8
        self.chrom_name = ""
        self.SPAWN_QUAD = None

        self.bot_name = bot_name

        ai.setPower(5)

        self.bin_chromosome = None
        self.dec_chromosome = None
        self.current_loop = None
        self.current_loop_idx = 0
        self.current_gene_idx = 0

        self.spawn_score = 0
        self.score = 0
        self.SD = False
        self.movement_timer = -1.0

        self.framesPostDeath = 0
        self.feed_history = ['' * 5]
        self.last_death = ["null", "null"]
        self.last_kill = ["null", "null"]
        self.prior_death = ["null", "null"]
        self.crossover_completed = False

        self.generate_feelers(10)
        self.frames_dead = 0

        self.ping_server()
        print("server ping")

    def increment_gene_idx(self):
        self.current_gene_idx = (self.current_gene_idx + 1) \
                                % self.GENES_PER_LOOP
        return self.current_gene_idx

    def update_score(self):
        self.score = ai.selfScore()

    def initialize_cga(self, quadrant):
        new_bin_chromosome, new_name = self.req_chrom(int(quadrant))

        if new_bin_chromosome == "" and self.initialized:
            path = os.path.join(self.repo_root, 'data', '{}.json'.format(self.chrom_name))
            with open(path, 'r') as f:
                try:
                    self.bin_chromosome = json.loads(f.readlines()[-1])[1]
                except Exception as e:
                    self.fix_chrom_file(path)
                    self.bin_chromosome = json.loads(f.readlines()[-1])[1]

        else:
            self.bin_chromosome = new_bin_chromosome
        print("New Name: " + new_name)
        ftype = "a"

        if not self.initialized:
            self.chrom_name = str(uuid.uuid4())[:8]
            new_name = self.chrom_name
            self.bin_chromosome = Evolver.generate_chromosome()
            self.initialized = True
        elif new_name == "":
            try:
                # Rewrite if it is a single generation failed chromosome
                with open(os.path.join(self.repo_root, 'data', '{}.json'.format(self.chrom_name)), 'r') as f:
                    file_length = len(f.readlines())
                    print("Name: " + self.chrom_name)

                if file_length == 3:
                    ftype = "w"
                    print("Rewriting file for: " + self.chrom_name)

            except Exception as e:  # noqa: E722
                print(e)
                self.chrom_name = str(uuid.uuid4())[:8]
                print("Exception: " + self.chrom_name)

        if new_name != "":
            self.chrom_name = new_name
            ftype = "a"
            self.update_chrom_map()

        self.write_soul_data(self.SPAWN_QUAD, ftype, score=0.0)

        self.dec_chromosome = Evolver.read_chrome(self.bin_chromosome)

        self.last_kill = ["null", "null"]
        self.last_death = ["null", "null"]

        self.current_loop_idx = 0
        self.current_loop = self.dec_chromosome[0]
        self.current_gene_idx = 0

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

    def write_soul_data(self, quadrant, ftype="a", score=0.0):
        if score == 0.0:
            write_score = str(0.0)
        else:
            write_score = str(round(score, 3))

        output = [str(quadrant), self.bin_chromosome, write_score]
        print(f"Chromesome is: {output}")
        print(f"Score is: {write_score}")

        Evolver.write_chromosome_to_file(output, "{}.json"
                                         .format(self.chrom_name), ftype, repo_root)
        self.update_chrom_map()
        self.spawn_score = self.score

    def was_killed(self):
        if self.SPAWN_QUAD is None: # If passed spawn quadrant none
            print("Agent was passed with SPAWN_QUAD set to None")
            traceback_str = traceback.format_exc()
            fs = os.path.join(self.repo_root, 'tracebacks', 'None_somehow_passed_{}.txt'.format(self.chrom_name))
            with open(fs, "a") as f:
                f.write(f"Agent {bot_name} with chromosome {self.chrom_name} was passed with SPAWN_QUAD set to None\n")
                f.write(traceback_str)
            return 
        
        agent.update_score()

        print(f"Last death is {self.last_death}")
        print(f"Current Score: {self.score}")
        print(f"Spawn Score: {self.spawn_score}")

        life_score = self.score - self.spawn_score
        print(f"Score to log: {life_score}")
        if "null" in self.last_death: # If ran into wall, dont crossover
            print("self death")

            self.push_chrom(int(self.SPAWN_QUAD), self.chrom_name)
            self.write_soul_data(self.SPAWN_QUAD, "a", score=life_score)
            self.bin_chromosome = None
            self.SPAWN_QUAD = None

            return

        if ai.selfAlive() == 0 and self.crossover_completed is False:
            killer = self.get_mapping(self.last_death[0])

            chromosome_file_name = os.path.join(self.repo_root, 'data', '{}.json'.format(killer)) # Find killers chromosome
            
            print(f"{killer} killed {self.chrom_name}")

            with open(chromosome_file_name, 'r') as f: # Retrieve data from that chromosome
                try:
                    chromosome_data = json.loads(f.readlines()[-1])
                except Exception as e:
                    self.fix_chrom_file(chromosome_file_name)
                    chromosome_data = json.loads(f.readlines()[-1])

            new_chromosome = chromosome_data[1]
            quadrant = chromosome_data[0] # Get killers quadrant
            if quadrant == None: # If the killers quadrant was not yet initalized (ie: Agent was killed early on)
                quadrant = self.SPAWN_QUAD 

            cross_over_child = Evolver.crossover(
                self.bin_chromosome, new_chromosome)
            mutated_child = Evolver.mutate(cross_over_child, self.MUT_RATE)
            self.bin_chromosome = mutated_child  # Set for soul write

            self.write_soul_data(self.SPAWN_QUAD, "a", score=life_score)
            # POST New chromosome
            self.push_chrom(quadrant, self.chrom_name)  # TODO switch to
            #self.push_chrom(quadrant, self.chrom_name)

            # Prep for fetching new chromosome
            self.bin_chromosome = None  # Erase for new chromosome to load
            self.SPAWN_QUAD = None

            self.crossover_completed = True

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

        if agent.SPAWN_QUAD is None and self.agent_data["X"] != -1:
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

    def fix_chrom_file(self, path):
        with open(path, 'w') as file:
            # Move the pointer (similar to a cursor in a text editor) to the end of the file
            file.seek(0, os.SEEK_END)

            # This code means the following code skips the very last character in the file -
            # i.e. in the case the last line is null we delete the last line
            # and the penultimate one
            pos = file.tell() - 1

            # Read each character in the file one at a time from the penultimate
            # character going backwards, searching for a newline character
            # If we find a new line, exit the search
            while pos > 0 and file.read(1) != "\n":
                pos -= 1
                file.seek(pos, os.SEEK_SET)

            # So long as we're not at the start of the file, delete all the characters ahead
            # of this position
            if pos > 0:
                file.seek(pos, os.SEEK_SET)
                file.truncate()

def loop():
    global agent
    global bot_name
    if agent is None:
        agent = CoreAgent(bot_name)

    try:
        if ai.selfAlive() == 1:
            if agent.SPAWN_QUAD is None:
                print("Spawn Quadrant: {} ".format(agent.set_spawn_quad()))
                agent.spawn_score = ai.selfScore()
                agent.SD = False
                ai.setTurnSpeed(64.0)
                agent.update_chrom_map()

            if agent.SPAWN_QUAD is not None and agent.bin_chromosome is None:
                agent.initialize_cga(agent.SPAWN_QUAD)

            if agent.agent_data["X"] != ai.selfX() or agent.agent_data["Y"] != ai.selfY(): # If agent is moving update time
                agent.movement_timer = time.time()

            if agent.movement_timer == -1.0:
                agent.movement_timer = time.time()
                agent.SD = False
                print("Initial SD timer set")

            if time.time() - agent.movement_timer > 5.0 and not agent.SD: # If agent hasnt moved for 5 seconds, SD
                ai.selfDestruct()
                agent.SD = True
                print("SD'ing")

            if agent.bin_chromosome is not None:
                agent.frames_dead = 0

                agent.update_agent_data()
                agent.update_enemy_data()
                agent.update_bullet_data()
                agent.update_score()

                agent.crossover_completed = False
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
                agent.update_agent_data()
        else:
            if agent.SPAWN_QUAD is None and agent.agent_data["X"] != -1 and agent.agent_data["Y"] != -1: # If this agent has not already been processed
                agent.set_spawn_quad() # Set spawn quad
            if agent.SPAWN_QUAD is None: # This would imply that SPAWN_QUAD is somehow None but the agent has been processed
                return # Just skip to next loop
                try:
                    raise ValueError("Unexpected state: SPAWN_QUAD is None but agent has been processed")
                except ValueError as e:
                    print(str(e))
                    traceback_str = traceback.format_exc()
                    fs = os.path.join(agent.repo_root, 'tracebacks', 'unexpected_spawn_quad_none_{}.txt'.format(agent.chrom_name))
                    with open(fs, "a") as f:
                        f.write(f"Agent {bot_name} with chromosome {agent.chrom_name} encountered an unexpected state with SPAWN_QUAD set to None\n")
                        f.write(traceback_str)
                    ai.quitAI()

            if agent.bin_chromosome is None:
                agent.initialize_cga(agent.SPAWN_QUAD) # Make this a proper agent

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
            f.write(str(agent.current_loop))
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