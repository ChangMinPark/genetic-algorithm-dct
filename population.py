#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
 - Based on open source Genetic Algorithm written in Java:
  (https://github.com/memento/GeneticAlgorithm) 
 - Improved by refering to a paper, "Enhancement of image watermark retrieval 
  based on genetic algorithms", for image watermarking. 
'''

import numpy as np
from individual import Individual


class Population:
    def __init__(self, img_blk: np.int, msg: np.int, n_indiv: int):
        self._pop_size = n_indiv
        self._chromosome_len = 8 * 8
        self._individuals = [
            Individual(img_blk, msg) for _ in range(self._pop_size)
        ]
        self._fittest_score = 0

    def select_fittest(self) -> Individual:
        max_fit = float('-inf')
        max_fit_idx = 0
        for idx, indiv in enumerate(self._individuals):
            if max_fit <= indiv.get_fitness():
                max_fit = indiv.get_fitness()
                max_fit_idx = idx

        self._fittest_score = self._individuals[max_fit_idx].get_fitness()
        try:
            return self._individuals[max_fit_idx].clone()
        except RuntimeError as e:
            print(e)
        return None

    def select_second_fittest(self) -> Individual:
        max_fit1 = max_fit2 = 0
        for idx, indiv in enumerate(self._individuals):
            if indiv._fitness > self._individuals[max_fit1].get_fitness():
                max_fit2 = max_fit1
                max_fit1 = idx
            elif indiv._fitness > self._individuals[max_fit2].get_fitness():
                max_fit2 = idx

        try:
            return self._individuals[max_fit2].clone()
        except RuntimeError as e:
            print(e)
        return None

    def get_least_fittest_idx(self) -> int:
        min_fit = float('inf')
        min_fit_idx = 0
        for idx, indiv in enumerate(self._individuals):
            if min_fit >= indiv.get_fitness():
                min_fit = indiv.get_fitness()
                min_fit_idx = idx
        return min_fit_idx

    def get_fittest_idx(self) -> int:
        max_fit = float('-inf')
        max_fit_idx = 0
        for idx, indiv in enumerate(self._individuals):
            if max_fit <= indiv.get_fitness():
                max_fit = indiv.get_fitness()
                max_fit_idx = idx
        return max_fit_idx

    def calculate_fitness(self):
        for indiv in self._individuals:
            indiv.calculate_fitness()
        self.select_fittest()

    def get_pop_size(self) -> int:
        return self._pop_size

    def set_pop_size(self, pop_size: int) -> None:
        self._pop_size = pop_size

    def get_individuals(self) -> list:
        return self._individuals

    def set_individuals(self, individuals: list) -> None:
        self._individuals = individuals

    def get_chromosome_len(self) -> int:
        return self._chromosome_len

    def set_chromosome_len(self, chromosome_len: int) -> None:
        self._chromosome_len = chromosome_len

    def get_fittest_score(self) -> int:
        return self._fittest_score

    def set_fittest_score(self, fittest_score: int) -> None:
        self._fittest_score = fittest_score
