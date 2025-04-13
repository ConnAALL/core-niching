import random

class Evolver():
    @classmethod
    def crossover(cls, chromosome_1, chromosome_2):
        """
        Performs crossover between two chromosomes to create a child chromosome.
        
        This method implements two types of crossover:
        1. Single Point Crossover - Splits chromosomes at a random point and combines them
        2. Uniform Crossover - Creates a new chromosome by randomly selecting bits from parent chromosomes
        
        Parameters:
            chromosome_1: First parent chromosome (from killed player)
            chromosome_2: Second parent chromosome (from killer)
            
        Returns:
            A new child chromosome created by crossover
        """
        chances = random.randint(0, 1)  # Randomly select crossover type (0 for uniform, 1 for single point)
        child = None
        print(f"Killed player chromosome {chromosome_1}")
        print(f"Killer chromosome {chromosome_2}")
        
        # Single Point Crossover: Occurs strictly between genes
        if chances == 1: 
            # Split between jump gene and following action genes
            splice_point = random.randint(1, len(chromosome_1))
            chrome1_X = chromosome_1[0:splice_point]  # First part of chromosome_1
            chrome1_Y = chromosome_1[splice_point:]   # Second part of chromosome_1
            chrome2_X = chromosome_2[0:splice_point]  # First part of chromosome_2
            chrome2_Y = chromosome_2[splice_point:]   # Second part of chromosome_2

            # Create two potential children by combining parts from both parents
            child1 = chrome1_X + chrome2_Y  # First part of parent 1 + second part of parent 2
            child2 = chrome2_X + chrome1_Y  # First part of parent 2 + second part of parent 1

            # Randomly select one of the two potential children
            if random.randint(0, 1) == 1:
                child = child1
            else:
                child = child2

        # Uniform crossover - randomly select bits from each parent
        elif chances == 0:  
            new_chromosome = [] 
            for loop_index in range(len(chromosome_1)):
                # Loop containing 12 genes
                loop = [] 

                for gene_index in range(len(chromosome_1[loop_index])):
                    # A 9 bit representation of a jump or action gene
                    gene = ""  

                    # Start at one to not flip jump and actions identifiers 
                    for bit_index in range(0, 
                                           len(chromosome_1[loop_index]
                                               [gene_index])): 
                        bit = ""
                        # For each bit, randomly select from either parent
                        if 0 == random.randint(0, 1):
                            bit = \
                                chromosome_1[loop_index][gene_index][bit_index]
                        else:
                            bit = \
                                chromosome_2[loop_index][gene_index][bit_index]

                        # Always preserve the first bit (gene type identifier) from parent 1
                        if bit_index == 0:
                            bit = \
                                chromosome_1[loop_index][gene_index][bit_index]

                        gene += bit
                    loop.append(gene)
                new_chromosome.append(loop)

            child = new_chromosome
        
        else:
            print("Crossover error")

        # Preserve jump genes from the killed player for consistency
        for gene_index in range(len(child)):
            if cls.is_jump_gene(child[gene_index]):
                new_jump_gene = chromosome_1[0:5] + child[gene_index][5:]
                child[gene_index] = new_jump_gene
        print(f"New chromosome {child}")
        return child

    @classmethod
    def mutate(cls, chromosome, MUT_RATE):
        """
        Mutates a chromosome by randomly flipping bits according to mutation rate.
        
        Different mutation strategies are applied to jump genes vs. action genes:
        - For jump genes: Only mutate the loop number bits
        - For action genes: Preserve the first bit, mutate all other bits
        
        Parameters:
            chromosome: The chromosome to mutate
            MUT_RATE: Mutation rate (higher = less frequent mutations)
            
        Returns:
            A mutated version of the input chromosome
        """
        new_chromosome = [] 
        for loop_index in range(len(chromosome)):
            loop = [] 

            for gene_index in range(len(chromosome[loop_index])):
                gene = chromosome[loop_index][gene_index]
                new_gene = ""  
                
                # Mutate jump gene
                if cls.is_jump_gene(gene): 
                    # Preserve the first 5 bits (gene type identifier and conditional index)
                    new_gene += gene[0:5]

                    # In a jump gene, the only dynamic bits are the loop number bits
                    for bit in gene[5:]:  
                        # Randomly flip bits based on mutation rate
                        if 0 == random.randint(0, MUT_RATE):
                            bit = '1' if bit == '0' else '0'
                        new_gene += bit

                # Mutate action gene
                else:  
                    # Preserve the first bit (gene type identifier)
                    new_gene += gene[0] 
                    
                    # Action gene has dynamic bits after bit 0         
                    for bit in gene[1:]: 
                        # Randomly flip bits based on mutation rate
                        if 0 == random.randint(0, MUT_RATE):
                            bit = '1' if bit == '0' else '0'
                        new_gene += bit

                loop.append(new_gene)
            new_chromosome.append(loop)

        return new_chromosome

    @classmethod
    def is_jump_gene(cls, gene):
        """
        Determines if a gene is a jump gene or an action gene.
        
        Jump genes and action genes are distinguished by their first bit:
        - Jump gene: First bit is '1' (string) or False (boolean)
        - Action gene: First bit is '0' (string) or True (boolean)
        
        Parameters:
            gene: The gene to check
            
        Returns:
            True if the gene is a jump gene, False otherwise
        """
        if type(gene[0]) == bool:
            return gene[0] is False
        elif type(gene[0]) == str:
            return gene[0] == "1"

    @classmethod
    def read_chrome(cls, chrome):
        """
        Converts a binary chromosome representation to a decimal form that can be executed.
        
        This method parses the binary strings in the chromosome and converts them to:
        - Jump genes: [False, conditional_index, loop_number]
        - Action genes: [True, shoot, thrust, turn_quantity, turn_target]
        
        Parameters:
            chrome: Binary representation of a chromosome
            
        Returns:
            Decoded chromosome with genes in decimal format
        """
        loops = []
        for gene in chrome:
            loop = []
            for instruction_gene in gene:
                # Case for jump gene (first bit is '1')
                if instruction_gene[0] == '1': 
                    # Parse the conditional index from bits 1-4 (as binary to decimal)
                    conditional_index = int(instruction_gene[1:5], 2)
                    # Parse the loop number from bits 5+ (as binary to decimal)

                    # Structure: False (indicates jump gene), conditional index, jump to conditional index when the corresponding condition is fuffilled
                    loop.append([False, conditional_index])

                # Case for action gene (first bit is '0')
                else:  
                    # Parse individual action parameters from binary bits
                    shoot = bool(int(instruction_gene[1])) # Bit 2 is wether or not you should shoot
                    thrust = int(instruction_gene[2:4], 2) # Bit is the chance of thrusting (speed up for a frame), 00 = no thrust, 01 = 33% chance, 10 = 66% chance, 11 = 100% chance 
                    turn_quantity = int(instruction_gene[4:7], 2) # Make turn quantity with 3 bit integer in binary rep, bits 4-6, number 0-7
                    turn_target = int(instruction_gene[7:], 2) # Make turn target with 3 bit integer in binary rep, bits 6-9, number 0-7 all correspond to different targets

                    # Structure: True (indicates action gene), shoot, thrust, turn_quantity, turn_target
                    loop.append([True, shoot, thrust, turn_quantity,
                                turn_target])
            loops.append(loop)

        return loops
    
    @classmethod
    def generate_chromosome(cls):
        """
        Generates a new random chromosome for initial population.
        
        A chromosome consists of 14 loops with 8 genes per loop. Each gene is 9 bits:
        - First gene in each loop is always a jump gene (first bit = '1')
        - Other genes are action genes (first bit = '0')
        - Jump genes' bits 1-4 are the conditional index, bits 5+ are the loop number
        - Action genes' bits are: shoot (bit 1), thrust chance (bit 2-3), turn_quantity (bits 4-6), 
          and turn_target (bits 7-9)
        
        Returns:
            A randomly generated chromosome
        """
        chromosome = []
        for loop_index in range(14):
            loop = []
            for i in range(9): 
                gene = ""
                for j in range(10): 
                    # First gene in a loop is always a jump gene (bit 0 = '1')
                    if i == 0 and j == 0:  
                        gene += "1"
                    # Other genes are action genes (bit 0 = '0') 
                    elif j == 0:  
                        gene += "0"
                    # For jump genes, set conditional index to match the loop index (bits 1-4)
                    elif i == 0 and j == 1:  
                        # 4 bit 0 padding to format loop_index as 4-bit binary
                        gene += format(loop_index, '04b')  
                    # For jump genes, last 5 bits are all 0's, as there is no use for them
                    elif i == 0 and j > 5:
                        gene += "0"
                    # For action genes, randomly set all bits after the first
                    elif i > 0:  
                        gene += str(random.randint(0, 1))
                loop.append(gene)
            chromosome.append(loop)
        return chromosome
    
    @classmethod
    def make_max_turn(cls, chrome):
        modified = []
        for row in chrome:
            new_row = []
            for gene in row:
                if gene[0] != '1':  # Only modify if the gene does NOT start with '1'
                    gene = gene[:3] + '111' + gene[6:]  # Set bits 3, 4, 5 to '1'
                new_row.append(gene)
            modified.append(new_row)
        return modified