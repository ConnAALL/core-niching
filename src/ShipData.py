import math
import random
from Engine import libpyAI as ai


class ShipData:
    def __init__(self):
        self.agent_data = {
            "heading": float(ai.selfHeadingDeg()),
            "tracking": float(ai.selfTrackingDeg()),
            "X": -1,
            "Y": -1,
            "speed": float(ai.selfSpeed()),
            "head_feelers": [],
            "track_feelers": []
        }
        
        self.enemy_data = {
            "X": -1,
            "Y": -1,
            "direction": -1,
            "speed": -1,
            "heading": -1,
            "distance": -1,
            "angle_to_enemy": -1
        }

        self.bullet_data = {
            "X": -1,
            "Y": -1,
            "distance": -1,
            "angle_to_shot": -1
        }

    def update_agent_data(self):
        self.agent_data["X"] = int(ai.selfX())
        self.agent_data["Y"] = int(ai.selfY())
        self.agent_data["speed"] = float(ai.selfSpeed())
        self.agent_data["heading"] = float(ai.selfHeadingDeg())
        self.agent_data["tracking"] = float(ai.selfTrackingDeg())

    def generate_feelers(self, step):
        print("Generating feelers")
        for angle in range(0, 360, step):
            self.agent_data["track_feelers"].append(
                ai.wallFeeler(500, int(self.agent_data["tracking"] + angle)))
        for angle in range(0, 360, step):
            self.agent_data["head_feelers"].append(
                ai.wallFeeler(500, int(self.agent_data["heading"] + angle)))
        self.agent_data["heading"] = float(ai.selfHeadingDeg())
        self.agent_data["tracking"] = float(ai.selfTrackingDeg())

        print(self.agent_data)

    def update_enemy_data(self):
        closest_ship_id = int(ai.closestShipId())
        if closest_ship_id != -1:
            self.enemy_data["distance"] = float(ai.enemyDistanceId(closest_ship_id))
            self.enemy_data["X"] = int(ai.screenEnemyXId(closest_ship_id))
            self.enemy_data["Y"] = int(ai.screenEnemyYId(closest_ship_id))
            self.enemy_data["speed"] = float(ai.enemySpeedId(closest_ship_id))
            self.enemy_data["heading"] = float(ai.enemyHeadingDegId(closest_ship_id))
            self.enemy_data["angle_to_enemy"] = int(self.find_angle())
            self.enemy_data["direction"] = self.get_enemy_dir()
        else:
            self.enemy_data["distance"] = -1
            self.enemy_data["X"] = -1
            self.enemy_data["Y"] = -1
            self.enemy_data["speed"] = -1
            self.enemy_data["heading"] = -1
            self.enemy_data["angle_to_enemy"] = -1
            self.enemy_data["direction"] = -1

    def update_bullet_data(self):
        if ai.shotDist(0) > 0:
            self.bullet_data["distance"] = float(ai.shotDist(0))
            self.bullet_data["X"] = ai.shotX(0)
            self.bullet_data["Y"] = ai.shotY(0)
            self.bullet_data["angle_to_shot"] = self.find_angle("bullet")
        else:
            self.bullet_data["distance"] = -1
            self.bullet_data["X"] = -1
            self.bullet_data["Y"] = -1
            self.bullet_data["angle_to_shot"] = -1

    def find_angle(self, param=None):
        if param is None:
            new_enemy_x = self.enemy_data["X"] - self.agent_data["X"]
            new_enemy_y = self.enemy_data["Y"] - self.agent_data["Y"]
        else:
            new_enemy_x = self.bullet_data["X"] - self.agent_data["X"]
            new_enemy_y = self.bullet_data["Y"] - self.agent_data["Y"]
        enemy_angle = -1
        try:
            enemy_angle = math.degrees(math.atan(new_enemy_y / new_enemy_x))
        except:
            enemy_angle = 0
        angle_to_enemy = int(self.agent_data["heading"] - enemy_angle)
        return angle_to_enemy if angle_to_enemy < 360 - angle_to_enemy else angle_to_enemy - 360

    def wall_between_target(self):
        return ai.wallBetween(int(self.agent_data["X"]), int(self.agent_data["Y"]), int(self.enemy_data["X"]), int(self.enemy_data["Y"])) != -1

    def get_enemy_dir(self):
        direction = -1
        theta = None
        wall_pre_enemy = False
        shot_tolerance = random.randint(-5, 5)

        if self.enemy_data["distance"] != -1:
            x_dist_to_enemy = self.enemy_data["X"] - self.agent_data["X"]
            y_dist_to_enemy = self.enemy_data["Y"] - self.agent_data["Y"]
            theta = self.find_angle()
            wall_pre_enemy = self.wall_between_target()
        else:
            return -1

        if self.enemy_data["distance"] and x_dist_to_enemy > 0 and y_dist_to_enemy > 0 and not wall_pre_enemy:
            direction = 1
        elif self.enemy_data["distance"] and x_dist_to_enemy < 0 and y_dist_to_enemy > 0 and not wall_pre_enemy:
            direction = 2
        elif self.enemy_data["distance"] and x_dist_to_enemy < 0 and y_dist_to_enemy < 0 and not wall_pre_enemy:
            direction = 3
        elif self.enemy_data["distance"] and x_dist_to_enemy > 0 and y_dist_to_enemy < 0 and not wall_pre_enemy:
            direction = 4
        return direction
