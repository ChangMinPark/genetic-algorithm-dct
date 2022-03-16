#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
 - Based on open source Genetic Algorithm written in Java:
  (https://github.com/memento/GeneticAlgorithm) 
 - Improved by refering to a paper, "Enhancement of image watermark retrieval 
  based on genetic algorithms", for image watermarking. 
'''

import numpy as np

from ga_utils import Utils

# Whether to enable advanced strategy for initializing the first population.
ADV_1ST_POP = True 
EMB_SHIFT = 2

class Individual:
    def __init__(self, img_blk: np.array, msg: np.array):
        self._img_blk = img_blk
        self._dct_coef = Utils.dct2(img_blk)
        self._msg = msg
        self._chromosome_len = 8 * 8
        self._fitness = 0
        self._zigzag = self._get_zigzag()
        self._e_cap = self._get_embedding_capacity()
        if ADV_1ST_POP:
            self._chromosomes = self._generate_initial_chromosome()
        else:
            self._chromosomes = \
                np.random.choice(a=[0, 1], size=self._chromosome_len)

    def calculate_fitness(self) -> None:
        # Calculate the similarity between the original message and the
        # extracted message from watermarked DCT after rounds of IDCT and DCT
        dct_emb = self._embed_msg()
        idct_emb = Utils.idct2(dct_emb)
        idct_emb += self._chromosomes.reshape(8,8)
        ext_msg = self._extract_msg(Utils.dct2(idct_emb.astype(int)))

        self._fitness = 0
        for idx in range(len(self._msg)):
            if self._msg[idx] == ext_msg[idx]:
                self._fitness += 1

    def tostring(self) -> str:
        return '[chromosome=%s]' % (str(self._chromosomes * 1))

    def clone(self):
        new_indiv = Individual(self._img_blk, self._msg)
        new_indiv._chromosomes = np.copy(self._chromosomes)
        new_indiv._fitness = self._fitness
        return new_indiv

    def get_fitness(self) -> int:
        return self._fitness

    def get_chromosomes(self) -> np.array:
        return self._chromosomes

    def get_w_img_blk(self) -> np.array:
        dct_emb = self._embed_msg()
        idct_emb = Utils.idct2(dct_emb)
        idct_emb += self._chromosomes.reshape(8,8)
        return idct_emb.astype(np.uint8)

    # --------------------- #
    #   Private functions   #
    # --------------------- #
    def _generate_initial_chromosome(self) -> np.array:
        dct_emb = self._embed_msg()
        idct_emb = Utils.idct2(dct_emb).astype(int).reshape(8,8)
        img_blk = self._img_blk.flatten()
        idct_blk = idct_emb.flatten()
        return np.array( \
            [img_blk[idx] != idct_blk[idx] for idx in range(len(idct_blk))]) * 1

    def _get_embedding_capacity(self):
        # Positions in DCT coefficient where to ebed message
        positions = np.array([
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]).flatten()

        # Indices of a list in zigzag order
        zigzag = self._zigzag

        # Bit capacity for each position
        cap = [0] * sum(positions)
        n = len(self._msg) // sum(positions)
        r = len(self._msg) % sum(positions)
        for idx in range(len(cap)):
            cap[idx] = n
            cap[idx] += 1 if idx < r else 0

        # Apply capacity to the positions
        for idx in range(len(positions)):
            pos = zigzag[idx]
            if positions[pos] == 1:
                positions[pos] = cap.pop(0)
        return positions
    
    def _get_zigzag(self):
        '''
        Returns indices of AC coefficients for watermark storage in a zig-zag
        manner. In case of block operation mode, the indices are selected in a
        per one per block manner. Eg. for block = 8
            1 3 6 . . . . . 
            2 5 9 . . . . .
            4 8 . . . . . .
            7 . . . . . . . 
            . . . . . . . .
            . . . . . . . .
            . . . . . . . .
            . . . . . . . .
        '''
        idx = np.zeros(8 * 8).astype(np.uint8)
        i = 0
        for sc in range(8 * 2):
            cc, cr = sc, 1
            while cc > 0:
                if cc <= 8 and cr <= 8:
                    idx[i] = (cc - 1) * 8 + cr
                    i += 1
                cc -= 1
                cr += 1

        return idx - 1  # Subtract 1 to all items because index starts from 0

    def _embed_msg(self) -> np.array:
        '''
        Embed the given message to a DCT of a block and construct a 
        watermarked block

        :param dct: DCT of a micro block
        :param msg: binary message to embed
        :return: watermarked block
        '''
        dct_arr, msg_arr = self._dct_coef.flatten(), self._msg
        w_blk = np.zeros(len(dct_arr), dtype=np.float32)
        msg_idx = 0
        for i in range(len(dct_arr)):
            idx = self._zigzag[i]
            e_cap = self._e_cap[idx]
            dct = dct_arr[idx]

            if not e_cap == 0:
                msg_part = msg_arr[msg_idx:msg_idx + e_cap]
                msg_idx += e_cap

                # If chromosome is True, add 1 to integer part
                int_part = int(dct)
                float_part = dct - int_part
                dec = Utils.dec_to_binarr(abs(int_part), 8)

                # Add msg_part in xxx000xx in the middle of the DCT
                dec[EMB_SHIFT:e_cap + EMB_SHIFT] = msg_part
                if dct < 0:
                    dct = float_part - Utils.binarr_to_dec(dec)
                else:
                    dct = float_part + Utils.binarr_to_dec(dec)

            w_blk[idx] = dct
        return w_blk.reshape(8,8)

    def _extract_msg(self, dct: np.array) -> np.array:
        '''
        Extract a message embedded in the given DCT array of a block
        
        :param dct: DCT of a block
        :return: extracted message in binary form
        '''
        msg_arr = []
        dct_arr = dct.flatten()
        for i in range(len(dct_arr)):
            idx = self._zigzag[i]
            e_cap = self._e_cap[idx]
            dct = dct_arr[idx]
            if not e_cap == 0:
                dec = Utils.dec_to_binarr(abs(int(dct)), 8)
                msg_part = dec[EMB_SHIFT:e_cap + EMB_SHIFT]
                msg_arr.extend(msg_part)
        return msg_arr
