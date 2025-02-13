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
        loops = []
        for gene in chrome:
            loop = []
            for instruction_gene in gene:
                # Case for jump chrom
                if instruction_gene[0] == '1': 
                    conditional_index = int(instruction_gene[1:5], 2)
                    loop_number = int(instruction_gene[5:], 2)

                    # Structure: False, conditional index, jump to num
                    loop.append([False, conditional_index, loop_number])

                # Case for action chromosome
                else:  
                    shoot = bool(int(instruction_gene[1]))
                    thrust = bool(int(instruction_gene[2]))
                    turn_quantity = int(instruction_gene[3:6], 2)
                    turn_target = int(instruction_gene[6:], 2)

                    loop.append([True, shoot, thrust, turn_quantity,
                                turn_target])
            loops.append(loop)

        return loops

    @classmethod
    # A chromosome consists of 16 loops with 8 genes per loop. Each gene is 9 
    # bits. Jump/Action is dictated by the first bit -> 1 == Jump Gene
    def generate_chromosome(cls):
        chromosome = []
        for loop_index in range(16):
            loop = []
            for i in range(8): 
                gene = ""
                for j in range(9): 
                    # Jump gene construction
                    if i == 0 and j == 0:  
                        gene += "1"
                    elif j == 0:  
                        gene += "0"
                    # Predefined conditional numbers
                    elif i == 0 and j == 1:  
                        # 4 bit 0 padding
                        gene += format(loop_index, '04b')  
                    elif i == 0 and j > 4:
                        gene += str(random.randint(0, 1))
                    elif i > 0:  
                        gene += str(random.randint(0, 1))
                loop.append(gene)
            chromosome.append(loop)
        return chromosome

    @classmethod
    def write_chromosome_to_file(cls, chromosome, filename, ftype):
        dataPath = os.path.join(repo_root, 'data', filename)
        with open(dataPath, ftype) as file:
            file.write("\n")
            json.dump(chromosome, file)

    @classmethod
    def log_chromosome_history(cls, chromosome, chrome_number, filename, repo_root):
        dataPath = os.path.join(repo_root, 'data', 'chromosome_logs', filename)
        with open(dataPath, "a") as f:
            f.write("Iteration {}: {} \n".format(chrome_number, chromosome))
