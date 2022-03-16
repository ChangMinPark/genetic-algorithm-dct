#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
 - Based on open source Genetic Algorithm written in Java:
  (https://github.com/memento/GeneticAlgorithm) 
 - Improved by refering to a paper, "Enhancement of image watermark retrieval 
  based on genetic algorithms", for image watermarking. 
'''

import numpy as np
from scipy.fftpack import dct, idct
from math import log10, sqrt
import sys
import re

class Utils:
    def dec_to_binarr(num: int, n_bits: int = None) -> np.array:
        if n_bits is None:
            bin_str = bin(num).replace('0b', '')
            bin_arr = np.zeros(len(bin_str), dtype=bool)
            for i in range(len(bin_str)):
                if int(bin_str[i]) == 1:
                    bin_arr[len(bin_str) - i - 1] = True
            return bin_arr

        else:
            bin_arr = np.zeros(n_bits, dtype=bool)
            bin_str = bin(num).replace('0b', '')
            for idx in range(n_bits):
                if idx < len(bin_str):
                    num = bin_str[len(bin_str) - idx - 1]
                    bin_arr[idx] = False if num == '0' else True
            return bin_arr

    def binarr_to_dec(binarr: np.array) -> int:
        return binarr.dot(1 << np.arange(binarr.shape[-1]))

    def dct2(a):
        return dct(dct(a.T, norm='ortho').T, norm='ortho')

    def idct2(a):
        return idct(idct(a.T, norm='ortho').T, norm='ortho')

    def calculate_psnr(img1_arr: np.array, img2_arr: np.array) -> float:
        '''
        Calculate PSNR of the two images
        '''
        def check_size_err(e: str) -> None:
            err_words = ['operand', 'broadcast', 'together', 'shapes']
            e = str(e).strip()
            res = [err_word in e for err_word in err_words]
            if all(res):
                pattern = "[()@]"
                org_split = re.sub(pattern, '', e.split(' ')[-2]).split(',')
                mod_split = re.sub(pattern, '', e.split(' ')[-1]).split(',')

                org_size = org_split[0] + 'x' + org_split[1]
                mod_size = mod_split[0] + 'x' + mod_split[1]
                sys.exit("Please give same sized images. \
                        \n - ORG_IMG = %s, MOD_IMG = %s" %
                         (org_size, mod_size))
            else:
                sys.exit(e)

        try:
            # MSE: mean square error between the two parts
            mse = np.mean((img1_arr - img2_arr)**2)
        except Exception as e:
            check_size_err(e)

        if (mse == 0):  # MSE is zero means no noise is present in the signal .
            # Therefore PSNR have no importance.
            return 100
        max_pixel = 255.0
        psnr = 20 * log10(max_pixel / sqrt(mse))
        return psnr
