import copy
import random

class Memory:

    """
    Class representing main memory. A dictionary stores memory blocks as byte arrays.
    It stores only blocks that have been accessed. New blocks are initialized randomly
    """

    def __init__(self, block_size):
        self._block_size = block_size

        # Dictionary to store memory blocks. 
        # It has block numbers (address where the block starts) as keys and byte arrays as values
        self._data = {}

    def read_block(self, address):
        """read block from memory that contains the address"""
        block_nr = self._get_block_nr(address)

        if block_nr not in self._data:
            # if block is accessed the first time, initialize randomly
            self._initialize_block(block_nr)
        return copy.copy(self._data[block_nr])
    
    def write_block(self, address, data):
        """write block to memory that contains the address"""
        self._data[self._get_block_nr(address)] = data

    def _initialize_block(self, block_nr):
        values = [0] * self._block_size
        for i in range(self._block_size):
            # generate random byte
            values[i] = random.randint(0, 0xFF)
        self._data[block_nr] = values

    def _get_block_nr(self, address):
        """maps the address to it's block and returns the start address (block number) from that block"""
        return address - (address % self._block_size)

    def print(self):
        data_len = self._block_size * 2 + (self._block_size - 1)
        print(f"\nMemory ({len(self._data)} blocks of {self._block_size} bytes each):")
        print(f"\033[4m{'block':<18} | {'data':<{data_len}} \033[0m")        
        for key, value in sorted(self._data.items()):
            bytes_string = ' '.join(f"{byte:02x}" for byte in value)
            print(f"{key:018x} | {bytes_string}")
        print()