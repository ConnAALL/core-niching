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
            
        self.agent = agent                                # Reference to the agent executing the action
        self.shoot = gene[1]                              # Boolean - whether to fire weapon this tick
        self.thrust = 1 if gene[2] else 0                 # Convert boolean to int (1 = thrust on, 0 = off)
        self.turn_quantity = int((gene[3] + 0) * 15)     # Scaling factor for turn amount
        self.turn_target = gene[4]                        # Target to turn towards (0-7 encoded values)

        # Execute the actions immediately upon gene creation
        self.act()

    def turn(self):
        """
        Control the ship's turning behavior based on the turn_target parameter.
        
        This method implements 8 different turning strategies (0-7):
        - 0-1: Turn toward or away from the nearest wall
        - 2-3: Turn toward or away from the farthest wall
        - 4-5: Turn toward or away from the nearest enemy
        - 6-7: Turn toward or away from the nearest bullet
        
        The turn_quantity parameter controls how sharp the turn is.
        """

        # Use match-case statement to select turning behavior
        match self.turn_target:
            # Case 0: Turn toward the nearest wall
            case 0:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["head_feelers"])
                if angle < 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle > 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                    
            # Case 1: Turn away from the nearest wall
            case 1:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["head_feelers"])
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle < 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                    
            # Case 2: Turn toward tracking
            case 2:
                angle = self.agent.find_direction_diff()
                if angle < 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle > 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                    
            # Case 3: Turn against tracking
            case 3:
                angle = self.agent.find_direction_diff()
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                elif angle < 0:
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise
                    
            # Case 4: Turn toward the nearest enemy ship
            case 4:
                if self.agent.enemy_data["distance"] is not None:
                    if self.agent.enemy_data["angle_to_enemy"] < 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    elif self.agent.enemy_data["angle_to_enemy"] > 0:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise
                        
            # Case 5: Turn away from the nearest enemy ship
            case 5:
                if self.agent.enemy_data["distance"] is not None:
                    if self.agent.enemy_data["angle_to_enemy"] > 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    else:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise

            # Case 6: Turn away from the nearest bullet
            case 6:
                if self.agent.bullet_data["X"] != -1:  # Check if bullet is detected
                    if self.agent.bullet_data["angle_to_shot"] > 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    elif self.agent.bullet_data["angle_to_shot"] < 0:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise

            # Case 7: Turn away from the nearest bullet
            case 7:
                if self.agent.bullet_data["X"] != -1:  # Check if bullet is detected
                    if self.agent.bullet_data["angle_to_shot"] > 0:
                        ai.turn(-1 * self.turn_quantity)  # Turn clockwise
                    elif self.agent.bullet_data["angle_to_shot"] < 0:
                        ai.turn(self.turn_quantity)       # Turn counter-clockwise
                        

    def act(self):
        """
        Execute all actions defined by this gene in the game environment.
        
        This method:
        1. Applies thrust based on the thrust parameter
        2. Fires a shot if the shoot parameter is True
        3. Executes turning behavior based on turn parameters
        """
        # Apply thrust (0 = no thrust, 1 = thrust on)
        ai.thrust(self.thrust)
        
        # Fire weapon if shoot is True
        ai.fireShot() if self.shoot else None
        
        # Execute turning behavior
        self.turn()