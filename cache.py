from memory import Memory
import random

class Line:
    """Class representing a single cache line"""
    def __init__(self, line_size):
        self.block = 0x00               # start address of memory block currently stored in this cache line
        self.valid = False              # is data valid (or just not never set)
        self.dirty = False              # for write-back: is cache more current than main memory
        self.used = 0                   # for LRU replacement
        self.data = [0] * line_size     # actual data. line_size is be same as main memory block size

    def print(self):
        bytes_string = ' '.join(f"{byte:02x}" for byte in self.data)
        print(f"{self.block:018x} {self.valid} {self.dirty} {bytes_string}")
        print()

class Cache:
    """Class representing a cache"""

    def __init__(self, line_count, block_size, memory :Memory):
        self.memory = memory 
        self._line_count = line_count                   
        self._block_size = block_size
        self._lines = [Line(block_size)] * line_count

    def read(self, address):
        # translate address into block address and offset
        offset = address % self._block_size
        block = address - offset

        data = None
        for line in self._lines:
            if line.block == block and line.valid:
                # READ HIT!
                print("Read Hit!")
                data = line.data
                break
        
        if data is None:
            # READ MISS!
            print("Read Miss!")
            data = self.load_from_memory(address)

        return data[offset]
    
    def load_from_memory(self, address):
        """loads block from memory and stores in cache line. Returns loaded data"""
        
        # choose line to replace
        # TODO: implement LRU, choose random for now
        target_line :Line = self._lines[random.randint(0, self._line_count - 1)]

        # write-back currently stored block if dirty
        if target_line.dirty:
            self.memory.write_block(target_line.data)


        # do the load
        data = self.memory.read_block(address)
        target_line.block = address - (address % self._block_size)
        target_line.data = data
        target_line.valid = True

        target_line.print()
        return data
    

    def print(self):
        print(f"\nMemory ({len(self._data) * self._block_size} bytes in {len(self._data)} blocks):")

        for key, value in sorted(self._data.items()):
            bytes_string = ' '.join(f"{byte:02x}" for byte in value)
            print(f"{key:018x}: {bytes_string}")
        print()