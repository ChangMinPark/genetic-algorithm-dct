#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
 - Based on open source Genetic Algorithm written in Java:
  (https://github.com/memento/GeneticAlgorithm) 
 - Improved by refering to a paper, "Enhancement of image watermark retrieval 
  based on genetic algorithms", for image watermarking. 
'''

import sys
import random
import numpy as np

from ga_utils import Utils
from individual import Individual
from population import Population

NUM_INDIVIDUALS = 5
ENABLE_TWO_POINT = True
CRITICAL_VALUE = 10


class GeneticAlgoDCT:
    def __init__(self, img_blk: np.array, msg: np.array, \
                                            verbose: bool=False) -> None:
        self._check_img_blk(img_blk)
        self._img_blk = img_blk
        self._msg = msg
        self._max_score = len(msg)
        self._n_chromosomes = 8 * 8
        self.population = Population(img_blk, msg, NUM_INDIVIDUALS)
        self.gen_count = 0
        self._solved = False
        self._fittest = None
        self._second_fittest = None
        self._verbose = verbose

    def get_w_img_blk(self) -> tuple:
        if self._solved:
            w_img_blk = self.population.select_fittest().get_w_img_blk()
            return w_img_blk, self.gen_count
        else:
            return None, self.gen_count

    def run(self) -> None:
        if self._verbose:
            print('Population of %d individual(s).' \
                %(self.population.get_pop_size()))

        self.population.calculate_fitness()
        if self._verbose:
            print('Generation: %d, Fittest: %d' \
                %(self.gen_count, self.population.get_fittest_score()))
            self._show_chromosome_pool()

        while self.population.get_fittest_score() < \
            self._max_score * (100-CRITICAL_VALUE)/100:
            
            # Do selection and crossover
            self._selection()
            self._crossover()

            # Do mutation under a random probability
            if random.randint(0, 100) % 7 < 5:
                self._mutation()

            # Add fittest offstring to population
            self._add_fittest_offstring()

            # Calculate new fitness value
            self.population.calculate_fitness()
            if self._verbose:
                print('\nGeneration: %d, Fittest score: %d' \
                    %(self.gen_count, self.population.get_fittest_score()))

            # Show chromosome pool
            if self._verbose:
                self._show_chromosome_pool()
            self.gen_count += 1

        self._solved = True
        if self._verbose:
            print('\nSolution found in generation %d' % (self.gen_count))
            print('Index of winner Individual: %d' %
                  (self.population.get_fittest_idx()))
            print('Fitness: %d' % (self.population.get_fittest_score()))
            print(
                'chromosomes: %s' %
                (str(self.population.select_fittest().get_chromosomes() * 1)))

    # --------------------- #
    #   Private functions   #
    # --------------------- #
    def _reset(self):
        self.__init__(self._img_blk, self._msg, self._verbose)

    def _selection(self) -> None:
        self._fittest = self.population.select_fittest()
        self._second_fittest = self.population.select_second_fittest()

    def _crossover(self) -> None:
        # Select a random crossover points
        p1 = p2 = 0
        if ENABLE_TWO_POINT:
            rand1 = random.randint(0, self._n_chromosomes - 1)
            rand2 = random.randint(0, self._n_chromosomes - 1)
            p1, p2 = sorted([rand1, rand2])
        else:
            p2 = random.randint(0, self._n_chromosomes - 1)
        for idx in range(p1, p2):
            tmp = self._fittest.get_chromosomes()[idx]
            self._fittest.get_chromosomes()[idx] = \
                                self._second_fittest.get_chromosomes()[idx]
            self._second_fittest.get_chromosomes()[idx] = tmp

    def _mutation(self) -> None:
        # Flip values at the mutation point
        p1 = random.randint(0, self._n_chromosomes - 1)
        p2 = random.randint(0, self._n_chromosomes - 1)
        self._fittest.get_chromosomes()[p1] = 1 \
            if self._fittest.get_chromosomes()[p1] == 0 else 0
        self._second_fittest.get_chromosomes()[p2] = 1 \
            if self._second_fittest.get_chromosomes()[p2] == 0 else 0

        if ENABLE_TWO_POINT:
            p1 = random.randint(0, self._n_chromosomes - 1)
            p2 = random.randint(0, self._n_chromosomes - 1)
            self._fittest.get_chromosomes()[p1] = 1 \
                if self._fittest.get_chromosomes()[p1] == 0 else 0
            self._second_fittest.get_chromosomes()[p2] = 1 \
                if self._second_fittest.get_chromosomes()[p2] == 0 else 0

    def _get_fittest_offstring(self) -> Individual:
        if self._fittest.get_fitness() > self._second_fittest.get_fitness():
            return self._fittest
        else:
            return self._second_fittest

    def _add_fittest_offstring(self) -> None:
        self._fittest.calculate_fitness()
        self._second_fittest.calculate_fitness()
        least_fittest_idx = self.population.get_least_fittest_idx()
        self.population.get_individuals()[least_fittest_idx] = \
                                                self._get_fittest_offstring()

    def _show_chromosome_pool(self) -> None:
        print('==Chromosome Pool==')
        for idx, indiv in enumerate(self.population.get_individuals()):
            print('> Individual %d | %s |' % (idx, indiv.tostring()))
        print('================')

    def _check_img_blk(self, img_blk: np.array):
        if not img_blk.shape == (8, 8):
            sys.exit('Given image block has an incorrect size: %s' \
                                            %(str(img_blk.shape)))


def main():
    
    # Test with example data
    img_blk = np.array([[202, 203, 205, 207, 208, 207, 206, 206],
                        [203, 204, 206, 207, 208, 208, 207, 207],
                        [205, 205, 207, 208, 209, 209, 208, 208],
                        [206, 207, 208, 208, 209, 209, 209, 209],
                        [208, 207, 207, 208, 208, 208, 209, 209],
                        [208, 207, 207, 206, 206, 207, 208, 209],
                        [208, 207, 205, 205, 205, 206, 207, 208],
                        [207, 206, 205, 204, 204, 205, 206, 207]], dtype=np.uint8)

    watermark = '110101001101110110000110000011011111'
    watermark = [True if c == '1' else False for c in watermark]
    
    demo = GeneticAlgoDCT(img_blk, watermark, verbose=True)
    demo.run()
    w_img_blk, gen = demo.get_w_img_blk()
    print('\nWatermarked image block (PSNR: %d): \n%s' \
        %(Utils.calculate_psnr(img_blk, w_img_blk), str(w_img_blk)))
    print('\nDCT of watermarked image block: \n%s' %(str(Utils.dct2(w_img_blk))))
    

if __name__ == '__main__':
    main()
