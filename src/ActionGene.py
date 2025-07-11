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
        self.turn_quantity = int((gene[3] + 0) * 10)     # Scaling factor for turn amount
        # 0 = 0.0 (does not turn)
        # 1 = 2.9268
        # 2 = 2.9268
        # 3 = 4.000
        # 4 = 5.5384
        # 5 = 6.667
        # 6 = 8.1818
        # 7 = 8.7723
        self.turn_target = gene[4]                        # Target to turn towards (0-7 encoded values)
        # Execute the actions immediately upon gene creation
        self.act(gene)

    def angle_diff(self, a1: float, a2: float) -> float:
        """angle_diff Finds the difference between two angles

        Args:
            a1 (float): angle 1
            a2 (float): angle 2

        Returns:
            float: result of the difference between the two angles
        """        
        diff = a2 - a1
        comp_diff = a2 + 360 - a1
        if abs(diff) < abs(comp_diff):
            return diff
        return comp_diff

    def angle_add(self, a1: float, a2: float) -> float:
        """angle_add Adds two angles together

        Args:
            a1 (float): angle 1
            a2 (float): angle 2

        Returns:
            float: result of adding the two angles
        """     
        return (a1+a2+360) % 360

    def turn_to_degree(self, degree: float) -> None:
        """turn_to_degree Turns the bot to the desired heading

        Args:
            degree (float): Heading to turn to
        """
        starting = self.agent.agent_data["head_feelers"][0][1]
        delta = self.angle_diff(starting, degree)
        if abs(delta) > 0:
            if delta <= 0:
                for i in range(2):
                    ai.turn(-1 * self.turn_quantity)  # Turn clockwise
            else:
                for i in range(2):
                    ai.turn(self.turn_quantity)       # Turn counter-clockwise

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
        #ai.thrust(0)
        # Use match-case statement to select turning behavior
        match self.turn_target:
            # Case 0: Turn away from the nearest wall (heading)
            case 0:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["head_feelers"])
                self.turn_to_degree(self.angle_add(angle, 180))
                    
            # Case 1: Turn away from the nearest wall (tracking)
            case 1:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["track_feelers"])
                self.turn_to_degree(self.angle_add(angle, 180))

            # Case 2: Turn toward tracking
            case 2:
                angle = ai.selfTrackingDeg()
                self.turn_to_degree(angle)
                    
            # Case 3: Turn against tracking
            case 3:
                if self.agent.debug: 
                    print("At turn against tracking case, case 3")
                angle = ai.selfTrackingDeg()
                self.turn_to_degree(self.angle_add(angle, 180))
                    
            # Case 4: Turn toward the nearest enemy ship
            case 4:
                if self.agent.debug: 
                    print("At turn toward enemy ship case, case 4")
                if self.agent.enemy_data["distance"] is not None:
                    self.turn_to_degree(self.agent.enemy_data["angle_to_enemy"])                 
                        
            # Case 5: Turn away from the nearest enemy ship
            case 5:
                if self.agent.debug: 
                    print("At turn away from enemy ship case, case 5")
                if self.agent.enemy_data["distance"] is not None:
                    self.turn_to_degree(self.angle_add(self.agent.enemy_data["angle_to_enemy"], 180))  

            # Case 6: Turn toward the nearest bullet
            case 6:
                if self.agent.debug: 
                    print("At turn toward nearest bullet case, case 6")
                if self.agent.bullet_data["X"] != -1:  # Check if bullet is detected
                    self.turn_to_degree(self.agent.bullet_data["angle_to_shot"])
                        
            # Case 7: Turn away from the nearest bullet
            case 7:
                if self.agent.debug: 
                    print("At turn away from nearest bullet case, case 7")
                if self.agent.bullet_data["X"] != -1:  # Check if bullet is detected
                    self.turn_to_degree(self.angle_add(self.agent.bullet_data["angle_to_shot"], 180))               

    def act(self, gene):
        """
        Execute all actions defined by this gene in the game environment.
        1. Fires a shot if the shoot parameter is True
        2. Applies thrust based on the thrust parameter
        3. Executes turning behavior based on turn parameters
        """

        # Fire if shoot is True
        ai.fireShot() if self.shoot else None

        # Apply thrust (0 = no thrust, 1 = thrust on)
        ai.thrust(self.thrust)
        
        # Execute turning behavior
        self.turn()

