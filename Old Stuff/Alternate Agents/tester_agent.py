import libpyAI as ai
import math
import random
import sys
import traceback
from src.Evolver import Evolver
import requests


class CoreAgent:
    def __init__(self, bot_name):
        #self.QUEUE_ADDR = #Define queue address here
        self.MUT_RATE = 300
        self.GENES_PER_LOOP = 8

        self.bot_name = bot_name
        self.heading = float(ai.selfHeadingDeg())
        self.tracking = float(ai.selfTrackingDeg())
        self.headingFeelers = []
        self.trackingFeelers = []

        self.SPAWN_X = None
        self.SPAWN_Y = None
        self.SPAWN_QUAD = None

        self.X = -1
        self.Y = -1
        self.heading = 90.0
        self.speed = -1
        ai.setTurnSpeed(20.0)
        ai.setPower(8)

        self.bin_chromosome = None
        self.dec_chromosome = None
        self.current_loop = None
        self.chromosome_iteration = 0
        self.current_loop_idx = 0
        self.current_gene_idx = 0

        self.score = 0
        self.prev_score = 0
        self.framesPostDeath = 0
        self.feed_history = ['' * 5]
        self.last_death = ["null", "null"]
        self.last_kill = ["null", "null"]
        self.prior_death = ["null", "null"]
        self.crossover_completed = False

        self.enemy_dist = -1
        self.enemy_dir = -1
        self.enemy_x = -1
        self.enemy_y = -1
        self.enemy_speed = -1
        self.enemy_heading = -1
        self.closest_bullet_distance = -1
        self.shot_x = -1
        self.shot_y = -1
        self.angle_to_shot = -1

        self.initialize_cga()
        self.generate_feelers(10)
        print("Alive!")
        self.frames_dead = 0        

    def increment_gene_idx(self):
        self.current_gene_idx = (self.current_gene_idx + 1) \
                                % self.GENES_PER_LOOP
        return self.current_gene_idx

    def update_score(self):
        self.prev_score = self.score
        self.score = ai.selfScore()

    def update_agent_data(self):
        self.X = int(ai.selfX())
        self.Y = int(ai.selfY())
        self.speed = float(ai.selfSpeed())

    def update_enemy_data(self):
        closest_ship_id = int(ai.closestShipId())
        if closest_ship_id != -1:
            self.enemy_dist = float(ai.enemyDistanceId(closest_ship_id))
            self.enemy_x = int(ai.screenEnemyXId(closest_ship_id))
            self.enemy_y = int(ai.screenEnemyYId(closest_ship_id))
            self.enemy_speed = float(ai.enemySpeedId(closest_ship_id))
            self.enemy_heading = float(ai.enemyHeadingDegId(closest_ship_id))
            self.angle_to_enemy = int(self.find_angle())
            self.enemy_dir = self.get_enemy_dir()
        else:
            self.enemy_dist = -1
            self.enemy_x = -1
            self.enemy_y = -1
            self.enemy_speed = -1
            self.enemy_heading = -1
            self.angle_to_enemy = -1
            self.enemy_dir = -1

    def update_bullet_data(self):
        if ai.shotDist(0) > 0:
            self.closest_bullet_distance = float(ai.shotDist(0))
            self.shot_x = ai.shotX(0)
            self.shot_y = ai.shotY(0)
            self.angle_to_shot = self.find_angle("bullet")
        else:
            self.closest_bullet_distance = -1
            self.shot_x = -1
            self.shot_y = -1
            self.angle_to_shot = -1

    def generate_feelers(self, step):
        for angle in range(0, 360, step):
            self.trackingFeelers.append(ai.wallFeeler(500, int(self.tracking + angle)))
        for angle in range(0, 360, step):
            self.headingFeelers.append(ai.wallFeeler(500, int(self.heading + angle)))
        self.heading = float(ai.selfHeadingDeg())
        self.tracking = float(ai.selfTrackingDeg())

    def initialize_cga(self, input_chrome=Evolver.generate_chromosome()):
        self.chromosome_iteration += 1
        self.bin_chromosome = input_chrome
        self.dec_chromosome = Evolver.read_chrome(self.bin_chromosome)
        print("Chromosome: {}".format(self.bin_chromosome))

        self.last_kill = ["null", "null"]
        self.last_death = ["null", "null"]

        self.current_loop_idx = 0
        self.current_loop = self.dec_chromosome[0]
        self.current_gene_idx = 0

        Evolver.write_chromosome_to_file(self.bin_chromosome, "{}.txt".format(self.bot_name))
        Evolver.log_chromosome_history(self.bin_chromosome, self.chromosome_iteration,
                                      "{}_history.txt".format(self.bot_name))

    def process_server_feed(self):
        self.feed_history = []
        for i in range(5):
            serverMessage = ai.scanGameMsg(i)
            if self.bot_name in serverMessage \
                    and "ratio" not in serverMessage \
                    and "crashed" not in serverMessage \
                    and "entered" not in serverMessage:
                self.feed_history.append(serverMessage)

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

    def was_killed(self):
        print(self.last_death)

        if "null" in self.last_death:
            return
        if ai.selfAlive() == 0 and self.crossover_completed is False:
            new_chromosome_file_name = "data/{}.txt".format(self.last_death[0])
            new_chromosome = None

            with open(new_chromosome_file_name, 'r') as f:
                new_chromosome = eval(f.read())

            cross_over_child = Evolver.crossover(self.bin_chromosome, new_chromosome)
            mutated_child = Evolver.mutate(cross_over_child, self.MUT_RATE)
            print(mutated_child)
            self.initialize_cga(mutated_child)
            self.crossover_completed = True
            self.self_destructed = False

    def find_min_wall_angle(self, wallFeelers):
        min_wall = min(wallFeelers)
        min_index = wallFeelers.index(min_wall)
        angle = int(10 * min_index)
        return angle if angle < 180 else angle - 360

    def find_max_wall_angle(self, wallFeelers):
        max_wall = max(wallFeelers)
        max_index = wallFeelers.index(max_wall)
        angle = int(10 * max_index)
        return angle if angle < 180 else angle - 360

    def find_angle(self, param=None):
        if param is None:
            new_enemy_x = self.enemy_x - self.X
            new_enemy_y = self.enemy_y - self.Y
        else:
            new_enemy_x = self.shot_x - self.X
            new_enemy_y = self.shot_y - self.Y
        enemy_angle = -1
        try:
            enemy_angle = math.degrees(math.atan(new_enemy_y / new_enemy_x))
        except:
            enemy_angle = 0
        angle_to_enemy = int(self.heading - enemy_angle)
        return angle_to_enemy if angle_to_enemy < 360 - angle_to_enemy else angle_to_enemy - 360

    def check_conditional(self, conditional_index):
        min_wall_dist = min(self.headingFeelers)
        conditional_list = [self.speed < 6, self.speed == 0, self.enemy_dist < 50, self.headingFeelers[0] < 100,
                            self.enemy_dist < 150 and self.enemy_dir == 1,
                            self.enemy_dist < 150 and self.enemy_dir == 2,
                            self.enemy_dist < 100 and self.enemy_dir == 3,
                            self.enemy_dist < 100 and self.enemy_dir == 4,
                            min_wall_dist < 200, min_wall_dist < 75, min_wall_dist > 300, min_wall_dist < 150,
                            self.closest_bullet_distance < 100, self.closest_bullet_distance < 200,
                            self.closest_bullet_distance < 50, self.enemy_dist == -1]
        return conditional_list[conditional_index]

    def wall_between_target(self):
        return ai.wallBetween(int(self.X), int(self.Y), int(self.enemy_x), int(self.enemy_y)) != -1

    def get_enemy_dir(self):
        direction = -1
        theta = None
        wall_pre_enemy = False
        shot_tolerance = random.randint(-5, 5)

        if self.enemy_dist != -1:
            x_dist_to_enemy = self.enemy_x - self.X
            y_dist_to_enemy = self.enemy_y - self.Y
            theta = self.find_angle()
            wall_pre_enemy = self.wall_between_target()
        else:
            return -1

        if self.enemy_dist and x_dist_to_enemy > 0 and y_dist_to_enemy > 0 and not wall_pre_enemy:
            direction = 1
        elif self.enemy_dist and x_dist_to_enemy < 0 and y_dist_to_enemy > 0 and not wall_pre_enemy:
            direction = 2
        elif self.enemy_dist and x_dist_to_enemy < 0 and y_dist_to_enemy < 0 and not wall_pre_enemy:
            direction = 3
        elif self.enemy_dist and x_dist_to_enemy > 0 and y_dist_to_enemy < 0 and not wall_pre_enemy:
            direction = 4
        return direction

    def push_chrom(self, quadrant, chromosome):
        data = {"quadrant": quadrant, "chromo": chromosome}
        re = requests.post(self.QUEUE_ADDR + "post", json=data)

        if re.status_code == 200:
            print("Sucessfully pushed to QS")
        else:
            print("Error pushing to QS")

    def req_chrom(self, quadrant):
        re = requests.get(self.QUEUE_ADDR + "req_{}".format(quadrant))

        if re.json() == -1:
            print("No available chromosome, generating new chromosome")
            return Evolver.generate_chromosome()

        print("Succesfully recieved chromosome")
        return re.json()["chromosome"]

    def ping_server(self):
        requests.get(self.QUEUE_ADDR + "is_alive")


class ActionGene:
    def __init__(self, gene, agent):
        if gene[0] is False:
            print(gene)
            print("Unexpected action gene found")
            return None
        self.agent = agent
        self.shoot = gene[1]
        self.thrust = 1 if gene[2] else 0
        self.turn_quantity = int((gene[3] + 3) * 2)
        self.turn_target = gene[4]

        self.act()

    def turn(self):
        match self.turn_target:
            case 0:
                angle = agent.find_min_wall_angle(agent.headingFeelers)
                if angle < 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle > 0:
                    ai.turn(self.turn_quantity)
            case 1:
                angle = agent.find_min_wall_angle(agent.headingFeelers)
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle < 0:
                    ai.turn(self.turn_quantity)
            case 2:
                angle = agent.find_max_wall_angle(agent.headingFeelers)
                if angle < 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle > 0:
                    ai.turn(self.turn_quantity)
            case 3:
                angle = agent.find_max_wall_angle(agent.headingFeelers)
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle < 0:
                    ai.turn(self.turn_quantity)
            case 4:
                if agent.enemy_dist is not None:
                    if agent.angle_to_enemy < 0:
                        ai.turn(-1 * self.turn_quantity)
                    elif agent.angle_to_enemy > 0:
                        ai.turn(self.turn_quantity)
            case 5:
                if agent.enemy_dist is not None:
                    if agent.angle_to_enemy > 0:
                        ai.turn(-1 * self.turn_quantity)
                    else:
                        ai.turn(self.turn_quantity)
            case 6:
                if agent.shot_x != -1:
                    if agent.angle_to_shot < 0:
                        ai.turn(-1 * self.turn_quantity)
                    elif agent.angle_to_shot > 0:
                        ai.turn(self.turn_quantity)
            case 7:
                if agent.shot_x != -1:
                    if agent.angle_to_shot > 0:
                        ai.turn(-1 * self.turn_quantity)
                    elif agent.angle_to_shot < 0:
                        ai.turn(self.turn_quantity)

    def act(self):
        ai.thrust(self.thrust)
        ai.fireShot() if self.shoot else None
        self.turn()


def loop():
    global agent
    global bot_name
    if agent is None:
        agent = CoreAgent(bot_name)
    try:
        if ai.selfAlive() == 1:
            agent.frames_dead = 0
            agent.update_agent_data()
            agent.update_enemy_data()
            agent.update_bullet_data()
            agent.update_score()
            agent.crossover_completed = False
            gene = agent.current_loop[agent.current_gene_idx]


            if agent.SPAWN_QUAD is None:
                agent.SPAWN_X = agent.X - 4500
                agent.SPAWN_Y = agent.Y - 4500

                if agent.SPAWN_X >= 0 and agent.SPAWN_Y >= 0:
                    agent.SPAWN_QUAD = 1
                elif agent.SPAWN_X < 0 and agent.SPAWN_Y >= 0:
                    agent.SPAWN_QUAD = 2
                elif agent.SPAWN_X < 0 and agent.SPAWN_Y < 0:
                    agent.SPAWN_QUAD = 3
                else: 
                    agent.SPAWN_QUAD = 4


            print(agent.SPAWN_QUAD)

        else:
            agent.process_server_feed()
            agent.frames_dead += 1
            if agent.frames_dead >= 5:
                agent.was_killed()
                agent.frames_dead = -2000

    except Exception as e:
        print("Exception")
        print(str(e))
        traceback.print_exc()
        traceback_str = traceback.format_exc()
        with open("tracebacks/traceback_{}.txt".format(agent.bot_name), "w") as f:
            f.write(traceback_str)
            f.write(str(agent.bin_chromosome))
            f.write(str(agent.dec_chromosome))
            f.write(str(agent.current_loop))
        ai.quitAI()


# SLURM 01:NL210-Lin10138
def main():
    global bot_name
    bot_name = "CA_{}".format(sys.argv[1])
    global agent
    agent = None
    ai.start(
        loop, ["-name", bot_name, "-join", "localhost"])


if __name__ == "__main__":
    main()
