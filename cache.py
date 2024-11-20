from memory import Memory
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
        self.use = 0                    # use-bits for LRU replacement. Highest possible = line_count
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
        offset = address % self._block_size
        block = address - offset

        cacheline = None
        for line in self._lines:
            if line.block == block and line.valid:
                # READ HIT!
                cacheline = line
                break
        
        if cacheline is None:
            # READ MISS!
            return None

        self._updated_use_bits(cacheline)
        return cacheline.data[offset]

    def write(self, address, value):
        """if write-hit returns written value. if write-miss returns None"""

        offset = address % self._block_size
        block = address - offset
        
        cacheline = None
        for line in self._lines:
            if line.block == block and line.valid:
                # WRITE HIT
                cacheline = line
                break
        
        if not cacheline:
            # WRITE MISS
            return None

        # write byte to cache
        cacheline.data[offset] = value
        cacheline.dirty = True
        self._updated_use_bits(cacheline)
        return value
        
    
    def load(self, address):
        """stores data in cache line"""

        # choose line to replace (LRU)
        target_line = self._lines[0]
        for line in self._lines:
            if line.use < target_line.use:
                target_line = line
        
        if not target_line.dirty and target_line.valid:
            print(f"Drop block from cache {target_line.block:018x}")

        # write-back currently stored block if dirty
        if target_line.dirty and target_line.valid:
            print(f"Write-Back and drop from cache {target_line.block:018x}")
            self.memory.write_block(target_line.block, target_line.data)

        # do the load
        data = self.memory.read_block(address)
        target_line.block = address - (address % self._block_size)
        target_line.data = data
        target_line.valid = True
        self._updated_use_bits(target_line)
        print(f"Loaded new cache line for address {address:018x}")
        return
    
    def _updated_use_bits(self, line :Line):
        """sets line as the most recently used line and adjusts the use bit of all other lines accordingly"""
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
        # calculate number of digits needed to print dynamic length values
        data_len = self._block_size * 2 + (self._block_size - 1)
        use_len = math.ceil(math.log(self._line_count, 16))     # LRU used number printed in hex
        nr_len = math.ceil(math.log(self._line_count, 10))      # number of line printed in decimal
        
        print(f"\nCache ({len(self._lines)} lines of {self._block_size} bytes each):")
        print(f"\033[4m{' ':<{nr_len}} | {'stored block':<18} | v d {'u':<{use_len}} | {'data':<{data_len}} \033[0m")
        for line in self._lines:
            bytes_string = ' '.join(f"{byte:02x}" for byte in line.data)
            print(f"{line.number:>0{nr_len}} | {line.block:018x} | {line.valid:b} {line.dirty:b} {line.use:>0{use_len}x} | {bytes_string}")
        print()
