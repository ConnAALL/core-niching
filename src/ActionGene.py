from Engine import libpyAI as ai

class ActionGene:
    def __init__(self, chromosome, agent):
        """
        Initialize ActionGene with the full chromosome and execute behaviors.
        
        Args:
            chromosome: List of behavior lists, each containing multiple [is_action, shoot, thrust, turn_quantity, turn_target]
            agent: The agent instance this action is for
        """
        self.agent = agent
        self.chromosome = chromosome
        
        # Select a behavior list based on current situation
        selected_behavior = self.select_behavior()
        
        # Execute the selected behavior
        self.execute_behavior(selected_behavior)

    def select_behavior(self):
        """
        Select the most appropriate behavior list based on current situation.
        Returns a single behavior list containing multiple actions.
        """
        # Priority checks to determine which behavior to use
        if self.agent.bullet_data["X"] != -1:  # If bullet detected
            return self.chromosome[0]  # Use first behavior list for dodging
        elif self.agent.enemy_data["distance"] is not None:  # If enemy detected
            return self.chromosome[1]  # Use second behavior list for combat
        else:  # Default to wall avoidance
            return self.chromosome[2]  # Use third behavior list for navigation

    def execute_behavior(self, behavior_list):
        """
        Execute a list of behaviors sequentially.
        
        Args:
            behavior_list: List of [is_action, shoot, thrust, turn_quantity, turn_target] actions
        """
        # Choose a behavior from the list based on current conditions
        for behavior in behavior_list:
            # Extract behavior parameters
            shoot = behavior[0]
            thrust = 1 if behavior[1] else 0
            turn_quantity = int(behavior[2]) * 5  # Scale turning amount
            turn_target = behavior[3]
            
            # Execute the behavior
            self.execute_action(shoot, thrust, turn_quantity, turn_target)

    def execute_action(self, shoot, thrust, turn_quantity, turn_target):
        """Execute a single action with the given parameters."""
        # Handle shooting
        if shoot:
            ai.fireShot()
            
        # Handle thrust
        ai.thrust(thrust)
        
        # Handle turning based on target type
        if turn_target <= 3:  # Wall avoidance turning
            angle = self.agent.find_min_wall_angle(self.agent.agent_data["head_feelers"])
            if turn_target in [0, 2]:  # Turn away from closest wall
                if angle < 0:
                    ai.turn(-1 * turn_quantity)
                elif angle > 0:
                    ai.turn(turn_quantity)
            else:  # Turn towards furthest wall
                if angle > 0:
                    ai.turn(-1 * turn_quantity)
                elif angle < 0:
                    ai.turn(turn_quantity)
                    
        elif turn_target <= 5:  # Enemy tracking turning
            if self.agent.enemy_data["distance"] is not None:
                angle = self.agent.enemy_data["angle_to_enemy"]
                if turn_target == 4:  # Turn towards enemy
                    if angle < 0:
                        ai.turn(-1 * turn_quantity)
                    elif angle > 0:
                        ai.turn(turn_quantity)
                else:  # Turn away from enemy
                    if angle > 0:
                        ai.turn(-1 * turn_quantity)
                    elif angle < 0:
                        ai.turn(turn_quantity)
                        
        else:  # Bullet dodging turning
            if self.agent.bullet_data["X"] != -1:
                angle = self.agent.bullet_data["angle_to_shot"]
                if turn_target == 6:  # Turn towards bullet
                    if angle < 0:
                        ai.turn(-1 * turn_quantity)
                    elif angle > 0:
                        ai.turn(turn_quantity)
                else:  # Turn away from bullet
                    if angle > 0:
                        ai.turn(-1 * turn_quantity)
                    elif angle < 0:
                        ai.turn(turn_quantity)