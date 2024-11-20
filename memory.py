import random

class Memory:

    """
    Class representing main memory. A dictionary stores memory blocks as byte arrays.
    """

    def __init__(self, block_size):
        self._block_size = block_size

        # Dictionary to store memory blocks. Key is the block number (address where the block starts), value is a byte array
        self._data = {}

    def read_block(self, address):
        """read block from memory that contains the address"""
        
        start_address = self._get_block(address)
        print(f"reading memory block from: {start_address:#018x} to {start_address + self._block_size - 1:#018x}")

        if start_address not in self._data:
            # if block is accessed the first time, initialize randomly
            self._initialize_block(start_address)
        return self._data[start_address]
    
    
    def write_block(self, address, data):
        """write block to memory that contains the address"""
        print(f"writing to memory block: {self._get_block(address):#018x}")
        self._data[self._get_block(address)] = data

    def _initialize_block(self, start_address):
        """initializes memory block starting from start_address with random bytes"""
        values = [0] * self._block_size
        for i in range(0, self._block_size):
            values[i] = random.randint(0, 0xFF)
        
        self._data[start_address] = values

    def _get_block(self, address):
        """returns the start address from the block that contains the address"""
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
        if self._get_block(address) not in self._data:
            self._initialize_block(self._get_block(address))
        
        block = self._data[self._get_block(address)]
        return block[address % self._block_size]

    def write_byte(self, address, value):
        """write single byte to memory"""
        start_address = self._get_block(address)
        if start_address not in self._data:
            self._initialize_block(start_address)
        block = self._data[start_address]
        block[address % self._block_size] = value
        self._data[start_address] = block
