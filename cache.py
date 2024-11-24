from bus import Bus, BusMessage, BusMessageType
from enum import Enum
import copy
import math

class PendingTransactionException(Exception):
    pass

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
        self.state = LineState.invalid
        self.use = 0                    # use-bits for LRU replacement. The line with highest is most recently used
        self.pending = False              
        self.data = [0] * line_size     # actual data. line_size is be same as main memory block size


class Cache:
    """Fully associative, write-back and write-invalidate cache"""

    def __init__(self, number, line_count, block_size, bus :Bus):
        self._number = number
        self._bus = bus
        self._line_count = line_count                   
        self._block_size = block_size
        self._lines = [Line(number = i, line_size = block_size) for i in range(line_count)]
        self._pending_line = None

    
    def cpu_read(self, address) -> tuple[int, bool]:
        offset = address % self._block_size
        block = address - offset
        line = self._find_block(block)            
        
        if not line or line.state == LineState.invalid:
            # READ MISS
            hit = False
            message = BusMessage(BusMessageType.read, block)
            data, memory_access = self._bus.put_message(self, message)
            line = self._store(block, data)
            if not memory_access:
                # data came not from main memory, but from other cache!
                line.state = LineState.shared
            else:
                # no other cache has block
                line.state = LineState.exclusive
                # to simulate that it will take a while to load the value from main memory
                # we mark it pending for a few cycles (even though it is already there)
                line.pending = True
                self._pending_line = line
        else:
            # READ HIT
            hit = True

        self._updated_use_bits(line)
        return line.data[offset], hit

    
    def cpu_write(self, address, value) -> bool:
        offset = address % self._block_size
        block = address - offset
        line = self._find_block(block)     

        if not line or line.state == LineState.invalid:
            # WRITE MISS
            hit = False
            message = BusMessage(BusMessageType.read_w, block, value)
            data, memory_access = self._bus.put_message(self, message)
            line = self._store(block, data)
            if memory_access:
                # to simulate that it will take a while to load the value from main memory
                # we mark it pending for a few cycles (even though it is already there)
                line.pending = True
                self._pending_line = line
        else:
            # WRITE HIT
            hit = True
            if line.state == LineState.shared:
                # signal other cores that I want to write
                message = BusMessage(BusMessageType.upgr, block, value)
                self._bus.put_message(self, message)

        line.state = LineState.modified
        line.data[offset] = value
        return hit


    def react_to_bus(self, message :BusMessage):
        """snoop messages on bus and react by changing state and maybe respond with requested data"""

        line = self._find_block(message.block)
        if not line or line.state == LineState.invalid:
            # Cache dont has this block, no action required
            return
        
        if line.pending:
            # This cache is currently in the process of retrieving this block from main memory!
            # The sender has to wait until this transaction is finished and try again then.
            # The sender's CPU will catch this Exception, abort the instruction, and try again the next cycles.
            raise PendingTransactionException()
        
        match line.state:
            case LineState.shared:
                if message.type == BusMessageType.upgr:
                    # sender wants to write on a shared block, therefore invalidate own copy
                    line.state = LineState.invalid
                    return

            case LineState.exclusive:
                if message.type == BusMessageType.read:
                    line.state = LineState.shared
                elif message.type == BusMessageType.read_w:
                    line.state = LineState.invalid
                return copy.copy(line.data)

            case LineState.modified:
                if message.type == BusMessageType.read:
                    line.state = LineState.shared
                elif message.type == BusMessageType.read_w:
                    line.state = LineState.invalid
                
                # To transiion back to shared/invalid, write-back the modified value to main memory
                message = BusMessage(BusMessageType.write, line.block, line.data)
                self._bus.put_message(self, message)

                # Since I have a modified value it is crucial to respond to ensure
                # the other cache does not use the stale copy from main memory.
                return copy.copy(line.data)
            
    
    def _store(self, block, data):
        """stores given block in a cacheline"""

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
        """sets given line as the most recently used line and adjusts the use bits of all other lines accordingly"""
        if line.use == self._line_count - 1:
            # line is already marked as most recently used
            return
        old_use = line.use
        line.use = self._line_count - 1
        for other in self._lines:
            if other == line or other.use <= old_use:
                continue
            other.use -= 1

    def clear_pending(self):
        self._pending_line.pending = False
        self._pending_line = None

    def print(self):
        """overengineered pretty-printer for cache lines"""
        # calculate number of digits needed to print dynamic length values
        data_len = self._block_size * 2 + (self._block_size - 1)
        use_len = math.ceil(math.log(self._line_count, 16))     # LRU used number printed in hex
        nr_len = math.ceil(math.log(self._line_count, 10))      # number of line printed in decimal
        
        print(f"\nCache{self._number} ({len(self._lines)} lines of {self._block_size} bytes each):")
        print(f"\033[4m{' ':<{nr_len}} | {'stored block':<18} | state p {'u':<{use_len}} | {'data':<{data_len}}\033[0m")
        for line in self._lines:
            bytes_string = ' '.join(f"{byte:02x}" for byte in line.data)
            print(f"{line.number:>0{nr_len}} | {line.block:018x} | {line.state.name[0:5].upper():<5} {line.pending:b} {line.use:>0{use_len}x} | {bytes_string}")
        print()
