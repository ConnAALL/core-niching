import random

class Evolver():
    @classmethod
    def crossover(cls, chromosome_1, chromosome_2):
        child = []
        chances = random.randint(0, 1)

        # Single Point Crossover: between behavior lists
        if chances == 1:
            # Choose a random splice point between the behavior lists
            splice_point = random.randint(1, len(chromosome_1))
            child = chromosome_1[:splice_point] + chromosome_2[splice_point:]
            
            # Random chance to use the alternative crossover result
            if random.randint(0, 1) == 1:
                child = chromosome_2[:splice_point] + chromosome_1[splice_point:]

        # Uniform crossover: mix individual behaviors/bits
        elif chances == 0:
            for b_list_index in range(len(chromosome_1)):
                new_behavior_list = []
                
                for behavior_index in range(len(chromosome_1[b_list_index])):
                    # For each behavior, choose bits from either parent
                    new_behavior = ""
                    
                    for bit_index in range(len(chromosome_1[b_list_index][behavior_index])):
                        if random.randint(0, 1) == 0:
                            new_behavior += chromosome_1[b_list_index][behavior_index][bit_index]
                        else:
                            new_behavior += chromosome_2[b_list_index][behavior_index][bit_index]
                            
                    new_behavior_list.append(new_behavior)
                
                child.append(new_behavior_list)
        else:
            print("Crossover error")
            
        return child

    @classmethod
    def mutate(cls, chromosome, MUT_RATE):
        new_chromosome = []
        
        for b_list_index in range(len(chromosome)):
            new_behavior_list = []
            
            for behavior_index in range(len(chromosome[b_list_index])):
                behavior = chromosome[b_list_index][behavior_index]
                new_behavior = ""
                
                for bit_index in range(len(behavior)):
                    bit = behavior[bit_index]
                    
                    # Chance to mutate each bit based on mutation rate
                    if random.randint(0, MUT_RATE) == 0:
                        bit = '1' if bit == '0' else '0'
                        
                    new_behavior += bit
                    
                new_behavior_list.append(new_behavior)
                
            new_chromosome.append(new_behavior_list)
            
        return new_chromosome

    @classmethod
    def read_chrome(cls, chrome):
        """
        Decode a binary chromosome into behavior lists.
        Each behavior is encoded as an 8-bit string:
        - bit 0: shoot
        - bit 1: thrust
        - bits 2-4: turn_quantity
        - bits 5-7: turn_target
        """
        decoded = []
        
        for behavior_list in chrome:
            decoded_behaviors = []
            for behavior in behavior_list:
                # Extract components from binary string
                shoot = bool(int(behavior[0]))
                thrust = bool(int(behavior[1]))
                turn_quantity = int(behavior[2:5], 2)  # Convert 3 bits to 0-7
                turn_target = int(behavior[5:8], 2)    # Convert 3 bits to 0-7
                
                decoded_behaviors.append([shoot, thrust, turn_quantity, turn_target])
            decoded.append(decoded_behaviors)
        
        return decoded

    @classmethod
    def generate_chromosome(cls):
        """
        Generate a chromosome with three behavior lists, each behavior encoded in binary.
        Structure:
        - bit 0: shoot (0/1)
        - bit 1: thrust (0/1)
        - bits 2-4: turn_quantity (3 bits for 0-7)
        - bits 5-7: turn_target (3 bits for 0-7)
        """
        chromosome = []
        
        # Create 3 behavior lists (dodge, combat, navigate)
        for _ in range(3):
            behavior_list = []
            
            # Create 8 behaviors per list
            for _ in range(8):
                # Generate each component and convert to binary
                shoot = str(random.randint(0, 1))
                thrust = str(random.randint(0, 1))
                turn_quantity = format(random.randint(0, 7), '03b')  # 3 bits for 0-7
                turn_target = format(random.randint(0, 7), '03b')    # 3 bits for 0-7
                
                # Combine into 8-bit binary string
                behavior = shoot + thrust + turn_quantity + turn_target
                behavior_list.append(behavior)
                
            chromosome.append(behavior_list)
        
        return chromosome