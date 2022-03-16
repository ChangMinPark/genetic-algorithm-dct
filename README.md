# Genetic Algorithm DCT
Watermarking data in DCT coefficient has a significant challenge that the extracted data is different with the original embedded data (reference: ["Digital Watermarking and Steganography: Fundamentals and Techniques", section 7, Frank Y. Shih](https://researchwith.njit.edu/en/publications/digital-watermarking-and-steganography-fundamentals-and-technique-2)). This is caused by IDCT and DCT that are applied after embedding:
- **IDCT**: converts DCT coefficient to image block
- **DCT**: converts image block to DCT coefficient before extraction

Traditional approaches embed data to the least significant bits (LSB) of DCT coefficient and apply rounding. This little change directly in DCT coefficient causes inconsistency of data after IDCT and DCT. Aforementioned literature solves the problem using genetic algorithm, and the algorithm in this repository has been implemented based on that. 

In a case that data embedding shouldn't change at all such as hashes, a user may set target fitness score to max. Howerver, a performance in that case is not really great with this algorithm. It requires more number of generations and sometimes runs infinite.

# Test
Run the main file (**_ga.py_**) by running below command:
```sh
$ python3 ga.py
```
Details about each generation while generating the best fittest score will be printed to standard output.

In the algorithm, there are multiple parameters that a user can change to advance as needed:
> - **NUM_INDIVIDUALS**: A number of individuals = population (default: 5)
> - **CRITICAL_VALUE**: Critical value to set target fitness score (default: 10)
> - **EMB_SHIFT**: How many bits to shift to embed data for each coefficient point. For example, shifting 2 means skipping two least significant bits from the right and embed data from third LSB. (default: 2)
> - **ENABLE_TWO_POINT**: Whether to enable two point technique (default: True)
> - **ADV_1ST_POP**: Whether to enable advanced population initialization (Default: True)

To understand the parameters, please read general genetic algorithm and the literature mentioned. 
