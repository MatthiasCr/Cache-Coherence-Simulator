from memory import Memory
import random
import math

class Line:
    """
    Class holding data and metadata of a single cache line
    """
    def __init__(self, number, line_size):
        self.number = number            # internal cache line number
        self.block = 0x00               # start address of memory block currently stored in this cache line
        self.valid = False              # is data valid (or just not never set)
        self.dirty = False              # for write-back: is cache more current than main memory
        self.use = 0                    # for LRU replacement
        self.data = [0] * line_size     # actual data. line_size is be same as main memory block size


class Cache:
    """
    Class representing a cache
    """

    def __init__(self, line_count, block_size, memory :Memory):
        self.memory = memory 
        self._line_count = line_count                   
        self._block_size = block_size
        self._lines = [Line(number = i, line_size = block_size) for i in range(line_count)]

    def read(self, address):
        # translate address into block and offset
        offset = address % self._block_size
        block = address - offset

        cacheline = None
        for line in self._lines:
            if line.block == block and line.valid:
                # READ HIT!
                print("Read Hit!")
                cacheline = line
                break
        
        if cacheline is None:
            # READ MISS!
            print("Read Miss!")
            cacheline = self.load_from_memory(address)
        
        self.updated_use_bit(cacheline)
        return cacheline.data[offset]

    def write(self, address, value):
        # translate address into block and offset
        offset = address % self._block_size
        block = address - offset
        
        cacheline = None
        for line in self._lines:
            if line.block == block and line.valid:
                # WRITE HIT
                print("Write Hit!")
                cacheline = line
                break
        
        if not cacheline:
            # WRITE MISS
            print("Write Miss")
            cacheline = self.load_from_memory(address)
        
        # write byte to cache
        cacheline.data[offset] = value
        cacheline.dirty = True
        self.updated_use_bit(cacheline)
        return cacheline
        
    
    def load_from_memory(self, address):
        """loads block from memory and stores in cache line. Returns cacheline"""
        
        # TODO: implement LRU, choose random for now
        # 
        # rand = random.randint(0, self._line_count - 2)
        # target_line :Line = self._lines[rand]

        # choose line to replace
        target_line = self._lines[0]
        for line in self._lines:
            if line.use < target_line.use:
                target_line = line

        if target_line.valid and not target_line.dirty:
            print(f"Drop block {target_line.block:018x}")

        # write-back currently stored block if dirty
        if target_line.dirty and target_line.valid:
            print(f"Write Back block {target_line.block:018x}")
            self.memory.write_block(address, target_line.data)

        # do the load
        data = self.memory.read_block(address)
        target_line.block = address - (address % self._block_size)
        target_line.data = data
        target_line.valid = True
        return target_line
    
    def updated_use_bit(self, line :Line):
        """sets line as the most recently used line and decreaes the use bit of all other lines"""
        if line.use == self._line_count - 1:
            # line is already marked as most recently used
            return
        old_use = line.use
        line.use = self._line_count - 1
        for other in self._lines:
            if other == line or other.use <= old_use:
                continue
            other.use -= 1

    def print(self):
        """overengineered pretty-printer for the cache lines"""
        # calculate number of digits needed to print som values
        data_len = self._block_size * 2 + (self._block_size - 1)
        use_len = math.ceil(math.log(self._line_count, 16))     # LRU used number printed in hex
        nr_len = math.ceil(math.log(self._line_count, 10))      # number of line printed in decimal
        
        print(f"\nCache ({len(self._lines)} lines of {self._block_size} bytes each):")
        print(f"\033[4m{' ':<{nr_len}} | {'Block stored':<18} | v d {'u':<{use_len}} | {'Data':<{data_len}} \033[0m")
        for line in self._lines:
            bytes_string = ' '.join(f"{byte:02x}" for byte in line.data)
            print(f"{line.number:>0{nr_len}} | {line.block:018x} | {line.valid:b} {line.dirty:b} {line.use:>0{use_len}x} | {bytes_string}")
        print()
