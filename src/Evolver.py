import random
import os
import json


class Evolver():
    @classmethod
    def crossover(cls, chromosome_1, chromosome_2):
        chances = random.randint(0, 1)
        child = None

        # Single Point Crossover: Occurs strictly between genes
        if chances == 1: 
            # Split between jump gene and following action genes
            splice_point = random.randint(1, len(chromosome_1))
            chrome1_X = chromosome_1[0:splice_point]
            chrome1_Y = chromosome_1[splice_point:]
            chrome2_X = chromosome_2[0:splice_point]
            chrome2_Y = chromosome_2[splice_point:]

            child1 = chrome1_X + chrome2_Y
            child2 = chrome2_X + chrome1_Y

            if random.randint(0, 1) == 1:
                child = child1
            else:
                child = child2

        # Uniform crossover
        elif chances == 0:  
            new_chromosome = [] 
            for loop_index in range(len(chromosome_1)):
                # Loop containing 16 genes
                loop = [] 

                for gene_index in range(len(chromosome_1[loop_index])):
                    # A 9 bit representation of a jump or action gene
                    gene = ""  

                    # Start at one to not flip jump and actions 
                    for bit_index in range(0, 
                                           len(chromosome_1[loop_index]
                                               [gene_index])): 
                        bit = ""
                        if 0 == random.randint(0, 1):
                            bit = \
                                chromosome_1[loop_index][gene_index][bit_index]
                        else:
                            bit = \
                                chromosome_2[loop_index][gene_index][bit_index]

                        if bit_index == 0:
                            bit = \
                                chromosome_1[loop_index][gene_index][bit_index]

                        gene += bit
                    loop.append(gene)
                new_chromosome.append(loop)

            child = new_chromosome

        else:
            print("Crossover error")

        for gene_index in range(len(child)):
            if cls.is_jump_gene(child[gene_index]):
                new_jump_gene = chromosome_1[0:5] + child[gene_index][5:]
                child[gene_index] = new_jump_gene
        return child

    @classmethod
    def mutate(cls, chromosome, MUT_RATE):
        new_chromosome = [] 
        for loop_index in range(len(chromosome)):
            loop = [] 

            for gene_index in range(len(chromosome[loop_index])):
                gene = chromosome[loop_index][gene_index]
                new_gene = ""  
                if cls.is_jump_gene(gene): 
                    new_gene += gene[0:5]

                    # In a jump gene, the only dynamic bits are the loop number 
                    for bit in gene[5:]:  
                        if 0 == random.randint(0, MUT_RATE):
                            bit = '1' if bit == '0' else '0'
                        new_gene += bit

                # Action Gene
                else:  
                    new_gene += gene[0] 
                    # Action gene has dynamic bits after bit 0.         
                    for bit in gene[1:]: 
                        if 0 == random.randint(0, MUT_RATE):
                            bit = '1' if bit == '0' else '0'
                        new_gene += bit

                loop.append(new_gene)
            new_chromosome.append(loop)

        return new_chromosome

    @classmethod
    def is_jump_gene(cls, gene):
        if type(gene[0]) == bool:
            return gene[0] is False
        elif type(gene[0]) == str:
            return gene[0] == "1"

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