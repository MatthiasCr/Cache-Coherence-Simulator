import copy
from enum import Enum
from bus import Bus, BusMessage, BusMessageType
import math

class LineState(Enum):
    invalid = 0,
    shared = 1,
    exclusive = 2,
    modified = 3

class Line:
    """Class holding data and metadata of a single cache line"""
    def __init__(self, number, line_size):
        self.number = number            # internal cache line number
        self.block = 0x00               # which block is currently stored in this cache line
        self.valid = False              # is data valid (or just not never set)
        self.dirty = False              # for write-back: is cache more current than main memory
        self.state = LineState.invalid
        self.use = 0                    # use-bits for LRU replacement. Highest possible = line_count
        self.data = [0] * line_size     # actual data. line_size is be same as main memory block size


class Cache:
    """Fully associative, write-back and write-invalidate cache"""

    def __init__(self, number, line_count, block_size, bus :Bus):
        self._number = number
        self._bus = bus
        self._line_count = line_count                   
        self._block_size = block_size
        self._lines = [Line(number = i, line_size = block_size) for i in range(line_count)]
        
    
    def cpu_read(self, address):
        offset = address % self._block_size
        block = address - offset
        line = self._find_block(block)            
        
        if not line or line.state == LineState.invalid:
            # READ MISS
            hit = False
            message = BusMessage(BusMessageType.read, block)
            data, memory_access = self._bus.put_message(self, message)
            line = self._load_block(block, data)
            if not memory_access:
                # data came from other cache!
                line.state = LineState.shared
            else:
                # no other cache has block
                line.state = LineState.exclusive
        else:
            # READ HIT
            hit = True
            memory_access = False

        self._updated_use_bits(line)
        # notify cpu if there was memory access so it can skip the next few cycles to simulate waiting
        return line.data[offset], hit, memory_access


        # is block in cache?
            # Yes -> read hit: return value, state stays the same (S/E/M)
            # No (state invalid)
                # put READ on Bus
                    # bus sends message to other caches
                    # if one responds with a value, bus returns this value
                    # if no one answers, load from memory (and signal cpu to wait the next cycles)
    
    def cpu_write(self, address, value):
        offset = address % self._block_size
        block = address - offset
        line = self._find_block(block)     

        if not line or line.state == LineState.invalid:
            # WRITE MISS
            hit = False
            message = BusMessage(BusMessageType.read_w, block, value)
            data, memory_access = self._bus.put_message(self, message)
            line = self._load_block(block, data)
        else:
            # WRITE HIT
            hit = True
            memory_access = False
            if line.state == LineState.shared:
                # we dont have the block exclusive yet, invalidate the other caches
                message = BusMessage(BusMessageType.upgr, block, value)
                self._bus.put_message(self, message)

        line.state = LineState.modified
        line.data[offset] = value
        return hit, memory_access

        # is block in cache?
            # Yes -> write hit
                # what state has this block?
                    # Modified -> do the write and return, state stays the same
                    # Exclusive -> do the write and transition to Modified
                    # Shared -> put UPGR on the Bus. Do the write and transition to Modified
            # No (state invalid)
                # put READX on the Bus
                    # value comes either from memory or from other cache
                    # than do the write and transition to Modified
        return

    def react_to_bus(self, message :BusMessage):
        """snoop on messages on bus and react by changing state and maybe also responding with requested data"""

        line = self._find_block(message.block)
        if not line or line.state == LineState.invalid:
            # cache dont has this block (anymore), no need to do anything
            return
        
        if line.state == LineState.shared:
            if message.type == BusMessageType.upgr:
                # someone else wants to write, therefore invalidate own copy
                line.state = LineState.invalid
                return
        
        elif line.state == LineState.exclusive or line.state == LineState.modified:
            # currently I am an exclusive owner
            if message.type == BusMessageType.read:
                line.state = LineState.shared
            elif message.type == BusMessageType.read_w:
                line.state = LineState.invalid
            # respond with block so that other cache gets most current value
            return copy.copy(line.data)

                # What state has this block?
                    # Shared
                        # If READ -> do nothing, still shared
                        # If UPGR -> transition to invalid
                    # Exclusive
                        # If READ -> transition to shared & ANSWER WITH BLOCK
                        # If REAEDX -> transition to invalid & ANSWER WITH BLOCK
                    # Modified
                        # If READ -> transition to shared & ANSWER WITH BLOCK
                        # If READX -> transition to invalid & ANSWER WITH BLOCK

    
    def _load_block(self, block, data):
        """loads block that contains the address from memory and stores in cache"""

        # choose line to replace (LRU)
        target_line = self._lines[0]
        for line in self._lines:
            if line.state == LineState.invalid:
                target_line = line
                break
            if line.use < target_line.use:
                target_line = line

        # write-back currently stored block if modified
        if target_line.state == LineState.modified:
            message = BusMessage(BusMessageType.write, target_line.block, target_line.data)
            self._bus.put_message(self, message)

        # do the load
        target_line.block = block
        target_line.data = data
        self._updated_use_bits(target_line)
        return target_line
    
    def _find_block(self, block):
        # since cache is fully associative, block can be stored in any cacheline
        for line in self._lines:
            if line.block == block:
                return line
        return None


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
        """overengineered pretty-printer for cache lines"""
        # calculate number of digits needed to print dynamic length values
        data_len = self._block_size * 2 + (self._block_size - 1)
        use_len = math.ceil(math.log(self._line_count, 16))     # LRU used number printed in hex
        nr_len = math.ceil(math.log(self._line_count, 10))      # number of line printed in decimal
        
        print(f"\nCache{self._number} ({len(self._lines)} lines of {self._block_size} bytes each):")
        print(f"\033[4m{' ':<{nr_len}} | {'stored block':<18} | state {'u':<{use_len}} | {'data':<{data_len}}\033[0m")
        for line in self._lines:
            bytes_string = ' '.join(f"{byte:02x}" for byte in line.data)
            print(f"{line.number:>0{nr_len}} | {line.block:018x} | {line.state.name[0:5].upper():<5} {line.use:>0{use_len}x} | {bytes_string}")
        print()
