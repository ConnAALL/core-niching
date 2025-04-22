from Engine import libpyAI as ai
import random 
class ActionGene:
    def __init__(self, gene, agent):
        """
        Initialize an action gene that controls the ship's movement and actions.
        
        This class executes the behaviors encoded in action genes, translating
        the genetic representation into concrete actions in the game environment.
        
        Parameters:
            gene: A decoded action gene from the chromosome [True, shoot, thrust, turn_quantity, turn_target]
            agent: Reference to the agent/ship that will execute these actions
        """
        # Verify that this is actually an action gene (gene[0] should be True)
        if gene[0] is False:
            print(gene)
            print("Unexpected action gene found")
        turn_roll = random.randint(1, 3) # Random int 0-2
        self.agent = agent                                # Reference to the agent executing the action
        self.shoot = gene[1]                              # Boolean - whether to fire weapon this tick        
        self.thrust = 0                                   # Thrust starts at 0
        if gene[2] <= turn_roll and gene[2] > 0 and self.agent.agent_data["speed"] < 10:          # If we have a chance of thrusting this frame, thrust if we roll lower or equal to our chance, speed limit 10
            self.thrust = 1     
        self.turn_quantity = int((gene[3] + 0) * 15)     # Scaling factor for turn amount, turn amount doesnt directly correspond to degrees
        self.turn_target = gene[4]                        # Target to turn towards (0-7 encoded values)
        self.action_priority = gene[5]                       # 0 if we prioritize thrusting over turning on this action, else 1

        # Execute the actions immediately upon gene creation
        self.act(gene)

    def turn(self):
        """
        Control the ship's turning behavior based on the turn_target parameter.
        
        This method implements 8 different turning strategies (0-7):
        - 0-1: Turn away from the nearest wall
        - 2-3: Turn toward or away from agents tracking
        - 4-5: Turn toward or away from the nearest enemy
        - 6-7: Turn toward or away from the nearest bullet
        
        The turn_quantity parameter controls how sharp the turn is.
        """

        # Use match-case statement to select turning behavior
        match self.turn_target:
            # Case 0: Turn away from the nearest wall (heading)
            case 0:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["head_feelers"])
                max_wall_angle = self.agent.find_max_wall_angle(self.agent_data["track_feelers"]) # Turn towards farthest wall as a failsafe
                if self.agent.debug: 
                    print(f"At turn away wall heading case, case 0, wall angle: {angle}")
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle < 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                elif angle == 0 and max_wall_angle > 0: # If we are facing the closest wall, turn to farthest wall as a failsafe 
                    ai.turn(self.turn_quantity)
                elif angle == 0 and max_wall_angle < 0: # If we are facing the closest wall, turn to farthest wall as a failsafe 
                    ai.turn(self.turn_quantity * -1)
                else: # Otherwise just turn right
                    ai.turnRight(self.turn_quantity)
                    
            # Case 1: Turn away from the nearest wall (tracking)
            case 1:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["track_feelers"])
                max_wall_angle = self.agent.find_max_wall_angle(self.agent_data["track_feelers"]) # Turn towards farthest wall as a failsafe
                if self.agent.debug: 
                    print(f"At turn away wall tracking case, case 1, wall angle: {angle}")
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle < 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                elif angle == 0 and max_wall_angle > 0: # If we are facing the closest wall, turn to farthest wall as a failsafe 
                    ai.turn(self.turn_quantity)
                elif angle == 0 and max_wall_angle < 0: # If we are facing the closest wall, turn to farthest wall as a failsafe 
                    ai.turn(self.turn_quantity * -1)
                else: # Otherwise just turn right
                    ai.turnRight(self.turn_quantity)
                    
            # Case 2: Turn toward tracking
            case 2:
                if self.agent.debug: 
                    print("At turn toward tracking case, case 2")
                angle = self.agent.find_direction_diff()
                if angle < 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle > 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                    
            # Case 3: Turn against tracking
            case 3:
                if self.agent.debug: 
                    print("At turn against tracking case, case 3")
                angle = self.agent.find_direction_diff()
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle < 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                    
            # Case 4: Turn toward the nearest enemy ship
            case 4:
                if self.agent.debug: 
                    print("At turn toward enemy ship case, case 4")
                if self.agent.enemy_data["distance"] is not None:
                    if self.agent.enemy_data["angle_to_enemy"] < 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    elif self.agent.enemy_data["angle_to_enemy"] > 0:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise
                        
            # Case 5: Turn away from the nearest enemy ship
            case 5:
                if self.agent.debug: 
                    print("At turn away from enemy ship case, case 5")
                if self.agent.enemy_data["distance"] is not None:
                    if self.agent.enemy_data["angle_to_enemy"] > 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    else:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise

            # Case 6: Turn toward the nearest bullet
            case 6:
                if self.agent.debug: 
                    print("At turn toward nearest bullet case, case 6")
                if self.agent.bullet_data["X"] != -1:  # Check if bullet is detected
                    if self.agent.bullet_data["angle_to_shot"] < 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    elif self.agent.bullet_data["angle_to_shot"] > 0:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise
                        
            # Case 7: Turn away from the nearest bullet
            case 7:
                if self.agent.debug: 
                    print("At turn away from nearest bullet case, case 7")
                if self.agent.bullet_data["X"] != -1:  # Check if bullet is detected
                    if self.agent.bullet_data["angle_to_shot"] > 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    elif self.agent.bullet_data["angle_to_shot"] < 0:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise
                        

    def act(self, gene):
        """
        Execute all actions defined by this gene in the game environment.
        1. Fires a shot if the shoot parameter is True
        2. Applies thrust based on the thrust parameter
        3. Executes turning behavior based on turn parameters
        """

        # Fire if shoot is True
        ai.fireShot() if self.shoot else None

        # Turning and thrusting must be mutually exclusive
        if self.thrust == 1 and gene[3] > 0 and self.action_priority == 0: 
                ai.thrust(self.thrust)
                return
        elif self.thrust == 1 and gene[3] > 0 and self.action_priority == 1:
                self.turn()
                return

        # Apply thrust (0 = no thrust, 1 = thrust on)
        ai.thrust(self.thrust)
        
        # Execute turning behavior
        self.turn()
