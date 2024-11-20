import random

class Memory:

    """
    Class representing main memory. A dictionary stores memory blocks as byte arrays.
    It stores only blocks that have been accessed. All blocks are randomly initialized
    """

    def __init__(self, block_size):
        self._block_size = block_size

        # Dictionary to store memory blocks. 
        # It has block numbers (address where the block starts) as keys and byte arrays as values
        self._data = {}

    def read_block(self, address):
        """read block from memory that contains the address"""
        
        block_nr = self._get_block_nr(address)
        print(f"reading memory block: {block_nr:#018x}")

        if block_nr not in self._data:
            # if block is accessed the first time, initialize randomly
            self._initialize_block(block_nr)
        return self._data[block_nr]
    
    def write_block(self, address, data):
        """write block to memory that contains the address"""
        
        print(f"writing to memory block: {self._get_block_nr(address):#018x}")
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
        print(f"\nMemory ({len(self._data) * self._block_size} bytes in {len(self._data)} blocks):")
        for key, value in sorted(self._data.items()):
            bytes_string = ' '.join(f"{byte:02x}" for byte in value)
            print(f"{key:018x}: {bytes_string}")
        print()
    

    # the following functions are only included for debugging purposes
    # reading/writing single bytes is never used in the project, since the cache only reads/writes entire blocks
    def read_byte(self, address):
        """read single byte from memory"""
        if self._get_block_nr(address) not in self._data:
            self._initialize_block(self._get_block_nr(address))
        
        block = self._data[self._get_block_nr(address)]
        return block[address % self._block_size]

    def write_byte(self, address, value):
        """write single byte to memory"""
        block_nr = self._get_block_nr(address)
        if block_nr not in self._data:
            self._initialize_block(block_nr)
        block = self._data[block_nr]
        block[address % self._block_size] = value
        self._data[block_nr] = block
