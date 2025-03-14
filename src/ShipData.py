import math
import random
from Engine import libpyAI as ai


class ShipData:
    def __init__(self):
        """
        Initialize the ship data and sensor systems.
        
        This class handles all the data collection and sensor reading for the ship,
        including wall detection, enemy tracking, and bullet detection.
        
        Feelers are sensor lines projected from the ship to detect objects like walls.
        They are defined by distance and angle:
        - distance: the length of the projection line to "feel" for objects
        - angle: the direction the feeler is drawn at in degrees

        Returns 1 if there is a wall from the player's ship at the given angle and distance or 0 if not.
        """

        # So 360 feelers from angle 0-359, all with a dist of 500, 
        # will cover a full 360 degree radius around the ship for a distance of 500 units

        self.agent_data = {
            "heading": float(ai.selfHeadingDeg()), # Direction the ship is pointed
            "tracking": float(ai.selfTrackingDeg()), # The actual direction the ship is going
            "X": -1, # Xpos
            "Y": -1, # Ypos
            "speed": float(ai.selfSpeed()), # Speed calculated by sqrt(pow(vel.x,2)+pow(vel.y,2))
            "head_feelers": [], # Feelers to determine heading
            "track_feelers": [] # Feelers to determine tracking
        }
        
        # Structure to store information about the nearest enemy ship
        self.enemy_data = {
            "X": -1,               # X position of enemy
            "Y": -1,               # Y position of enemy
            "direction": -1,       # Direction quadrant (1-4) of enemy relative to agent
            "speed": -1,           # Speed of enemy ship
            "heading": -1,         # Heading direction of enemy ship in degrees
            "distance": -1,        # Distance to enemy ship
            "angle_to_enemy": -1   # Angle between agent's heading and enemy position
        }

        # Structure to store information about the nearest bullet/projectile
        self.bullet_data = {
            "X": -1,               # X position of bullet
            "Y": -1,               # Y position of bullet
            "distance": -1,        # Distance to bullet
            "angle_to_shot": -1    # Angle between agent's heading and bullet position
        }

    def update_agent_data(self):
        """
        Update the agent's positional data from the game engine.
        
        Retrieves the current position, speed, heading, and tracking information
        from the libpyAI interface.
        """
        self.agent_data["X"] = int(ai.selfX())
        self.agent_data["Y"] = int(ai.selfY())
        self.agent_data["speed"] = float(ai.selfSpeed())
        self.agent_data["heading"] = float(ai.selfHeadingDeg())
        self.agent_data["tracking"] = float(ai.selfTrackingDeg())
        
        self.generate_feelers(10)

    def generate_feelers(self, step):
        """
        Generate sensor feelers around the ship to detect nearby objects.
        
        This creates two sets of feelers:
        1. track_feelers: Based on ship's tracking direction (actual movement)
        2. head_feelers: Based on ship's heading direction (where it's pointing)
        
        Parameters:
            step: Angular increment in degrees between feelers (smaller = more feelers)
        """
        # Generate feelers from angle 0 to 359 every stepth degree, range of 500
        #print("Generating feelers")
        self.agent_data["track_feelers"] = []
        self.agent_data["head_feelers"] = []
        for angle in range(0, 360, step):
            self.agent_data["track_feelers"].append(
                ai.wallFeeler(500, int(self.agent_data["tracking"] + angle)))
        for angle in range(0, 360, step):
            self.agent_data["head_feelers"].append(
                ai.wallFeeler(500, int(self.agent_data["heading"] + angle)))
        self.agent_data["heading"] = float(ai.selfHeadingDeg())
        self.agent_data["tracking"] = float(ai.selfTrackingDeg())

        #print(self.agent_data)

    def update_enemy_data(self):
        """
        Update information about the closest enemy ship.
        
        This method:
        1. Identifies the closest enemy ship
        2. Updates all enemy-related data (position, distance, etc.)
        3. Calculates relative angles and direction quadrant
        4. Sets default values (-1) if no enemy is detected
        """
        closest_ship_id = int(ai.closestShipId())
        if closest_ship_id != -1:
            # Enemy ship detected, update all enemy data
            self.enemy_data["distance"] = float(ai.enemyDistanceId(closest_ship_id))
            self.enemy_data["X"] = int(ai.screenEnemyXId(closest_ship_id))
            self.enemy_data["Y"] = int(ai.screenEnemyYId(closest_ship_id))
            self.enemy_data["speed"] = float(ai.enemySpeedId(closest_ship_id))
            self.enemy_data["heading"] = float(ai.enemyHeadingDegId(closest_ship_id))
            self.enemy_data["angle_to_enemy"] = int(self.find_angle())
            self.enemy_data["direction"] = self.get_enemy_dir()
        else:
            # No enemy ship detected, set default values
            self.enemy_data["distance"] = -1
            self.enemy_data["X"] = -1
            self.enemy_data["Y"] = -1
            self.enemy_data["speed"] = -1
            self.enemy_data["heading"] = -1
            self.enemy_data["angle_to_enemy"] = -1
            self.enemy_data["direction"] = -1

    def update_bullet_data(self):
        """
        Update information about the closest bullet/projectile.
        
        This method:
        1. Checks if any bullet is within detection range
        2. Updates bullet position and trajectory data
        3. Sets default values (-1) if no bullet is detected
        """
        if ai.shotDist(0) > 0:
            # Bullet detected, update bullet data
            self.bullet_data["distance"] = float(ai.shotDist(0))
            self.bullet_data["X"] = ai.shotX(0)
            self.bullet_data["Y"] = ai.shotY(0)
            self.bullet_data["angle_to_shot"] = self.find_angle("bullet")
        else:
            # No bullet detected, set default values
            self.bullet_data["distance"] = -1
            self.bullet_data["X"] = -1
            self.bullet_data["Y"] = -1
            self.bullet_data["angle_to_shot"] = -1

    def find_angle(self, param=None):
        """
        Calculate the angle between the ship's heading and a target (enemy or bullet).
        
        This method:
        1. Calculates the relative position of the target
        2. Uses arctangent to find the angle
        3. Normalizes the angle to be between -180 and 180 degrees
        
        Parameters:
            param: If "bullet", calculate angle to bullet; otherwise calculate angle to enemy
            
        Returns:
            Normalized angle in degrees to the target
        """
        if param is None:
            # Calculate vector to enemy
            new_enemy_x = self.enemy_data["X"] - self.agent_data["X"]
            new_enemy_y = self.enemy_data["Y"] - self.agent_data["Y"]
        else:
            # Calculate vector to bullet
            new_enemy_x = self.bullet_data["X"] - self.agent_data["X"]
            new_enemy_y = self.bullet_data["Y"] - self.agent_data["Y"]
        enemy_angle = -1
        try:
            # Calculate angle using arctangent
            enemy_angle = math.degrees(math.atan(new_enemy_y / new_enemy_x))
        except:
            enemy_angle = 0
        # Calculate relative angle to the target
        angle_to_enemy = int(self.agent_data["heading"] - enemy_angle)
        # Normalize angle to be between -180 and 180 degrees
        return angle_to_enemy if angle_to_enemy < 360 - angle_to_enemy else angle_to_enemy - 360

    def wall_between_target(self):
        """
        Check if there's a wall between the ship and the enemy.
        
        Uses the libpyAI wallBetween function to detect obstacles between 
        the agent's position and the target enemy's position.
        
        Returns:
            True if a wall is detected between agent and enemy, False otherwise
        """
        return ai.wallBetween(int(self.agent_data["X"]), int(self.agent_data["Y"]), int(self.enemy_data["X"]), int(self.enemy_data["Y"])) != -1

    def get_enemy_dir(self):
        """
        Determine the directional quadrant of the enemy relative to the agent.
        
        This method:
        1. Calculates the relative position of the enemy (x,y coordinates)
        2. Determines which quadrant the enemy is in (1-4)
        3. Checks if there's a wall between agent and enemy
        
        Returns:
            Direction quadrant (1-4) or -1 if enemy not detected or behind wall:
            1: Top-right quadrant (enemy is NE of agent)
            2: Top-left quadrant (enemy is NW of agent)
            3: Bottom-left quadrant (enemy is SW of agent)
            4: Bottom-right quadrant (enemy is SE of agent)
            -1: No enemy detected or wall between agent and enemy
        """
        direction = -1
        theta = None
        wall_pre_enemy = False
        shot_tolerance = random.randint(-5, 5)  # Random tolerance for shot calculations

        if self.enemy_data["distance"] != -1:
            # Calculate relative position of enemy
            x_dist_to_enemy = self.enemy_data["X"] - self.agent_data["X"]
            y_dist_to_enemy = self.enemy_data["Y"] - self.agent_data["Y"]
            theta = self.find_angle()
            # Check if there's a wall between agent and enemy
            wall_pre_enemy = self.wall_between_target()
        else:
            return -1

        # Determine which quadrant the enemy is in (only if no wall is in the way)
        if self.enemy_data["distance"] and x_dist_to_enemy > 0 and y_dist_to_enemy > 0 and not wall_pre_enemy:
            direction = 1  # Top-right quadrant
        elif self.enemy_data["distance"] and x_dist_to_enemy < 0 and y_dist_to_enemy > 0 and not wall_pre_enemy:
            direction = 2  # Top-left quadrant
        elif self.enemy_data["distance"] and x_dist_to_enemy < 0 and y_dist_to_enemy < 0 and not wall_pre_enemy:
            direction = 3  # Bottom-left quadrant
        elif self.enemy_data["distance"] and x_dist_to_enemy > 0 and y_dist_to_enemy < 0 and not wall_pre_enemy:
            direction = 4  # Bottom-right quadrant
        return direction