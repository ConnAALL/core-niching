from Engine import libpyAI as ai

class ActionGene:
    def __init__(self, gene, agent):
        if gene[0] is False:
            print(gene)
            print("Unexpected action gene found")
        self.agent = agent
        self.shoot = gene[1]
        self.thrust = 1 if gene[2] else 0
        self.turn_quantity = int((gene[3] + 0) * 5)  # Prev + 3 * 2
        self.turn_target = gene[4]

        self.act()

    def turn(self):
        match self.turn_target:
            case 0:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["head_feelers"])
                if angle < 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle > 0:
                    ai.turn(self.turn_quantity)
            case 1:
                angle = self.agent.find_min_wall_angle(self.agent.agent_data["head_feelers"])
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle < 0:
                    ai.turn(self.turn_quantity)
            case 2:
                angle = self.agent.find_max_wall_angle(self.agent.agent_data["head_feelers"])
                if angle < 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle > 0:
                    ai.turn(self.turn_quantity)
            case 3:
                angle = self.agent.find_max_wall_angle(self.agent.agent_data["head_feelers"])
                if angle > 0:
                    ai.turn(-1 * self.turn_quantity)
                elif angle < 0:
                    ai.turn(self.turn_quantity)
            case 4:
                if self.agent.enemy_data["distance"] is not None:
                    if self.agent.enemy_data["angle_to_enemy"] < 0:
                        ai.turn(-1 * self.turn_quantity)
                    elif self.agent.enemy_data["angle_to_enemy"] > 0:
                        ai.turn(self.turn_quantity)
            case 5:
                if self.agent.enemy_data["distance"] is not None:
                    if self.agent.enemy_data["angle_to_enemy"] > 0:
                        ai.turn(-1 * self.turn_quantity)
                    else:
                        ai.turn(self.turn_quantity)
            case 6:
                if self.agent.bullet_data["X"] != -1:
                    if self.agent.bullet_data["angle_to_shot"] < 0:
                        ai.turn(-1 * self.turn_quantity)
                    elif self.agent.bullet_data["angle_to_shot"] > 0:
                        ai.turn(self.turn_quantity)
            case 7:
                if self.agent.bullet_data["X"] != -1:
                    if self.agent.bullet_data["angle_to_shot"] > 0:
                        ai.turn(-1 * self.turn_quantity)
                    elif self.agent.bullet_data["angle_to_shot"] < 0:
                        ai.turn(self.turn_quantity)

    def act(self):
        ai.thrust(self.thrust)
        ai.fireShot() if self.shoot else None
        self.turn()
