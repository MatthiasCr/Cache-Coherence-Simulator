from cache import Cache
from enum import Enum
from memory import Memory
import util

class CpuState(Enum):
    ready = 0
    waiting_for_memory = 1
    finished = 2


class Cpu:
    """
    Class simulating a CPU/Core that executes memory traces
    """

    def __init__(self, number, file_path, cache :Cache):
        self._number = number                           # Number of CPU used for printing
        self._cache = cache
        self._traces_file = open(file_path, 'r')
        self.state = CpuState.ready
        self._waiting_cycles = 0                        # number of remaining cycles to wait
        self._waiting_callback = None                   # function that is executed when core finished waiting

    def handle_next_instruction(self):
        """this function is executed once in every cycle"""

        match self.state:
            case CpuState.finished: 
                return            
            
            case CpuState.waiting_for_memory:
                if self._waiting_cycles > 0:
                    # skip cycle to simulate waiting for memory access
                    self._waiting_cycles -= 1
                    print(f"CPU{self._number}: Waiting for Memory")
                    return
                elif self._waiting_cycles == 0:
                    # finally, the waiting is done :)
                    # now execute the callback to load the data into cache and read/write it
                    self._waiting_callback()
                    print(f"CPU{self._number}: Memory access completed")
                    self.state = CpuState.ready
                    return

            case CpuState.ready:
                # read next instruction   
                
                line = self._traces_file.readline()

                if not line:
                    self.state = CpuState.finished
                    return
                
                if line.startswith('#'):
                    # line is commented, read next
                    return self.handle_next_instruction()

                # parse instruction
                parts = line.split()

                try:
                    command = parts[0]
                    address = int(parts[1], 16)
                    assert(util.is_valid_address(address))
                    assert(command == 'R' or command == 'W')

                    if parts[0] == 'R':
                        return self._handle_read(address)
                    elif parts[0] == 'W':
                        value = int(parts[2], 16)
                        return self._handle_write(address, value)
                except:
                    raise Exception("Traces File Syntax Error")
    

    def _handle_read(self, address):
        value = self._cache.read(address)
        if value is None:
            # READ MISS!

            self.state = CpuState.waiting_for_memory
            self._waiting_cycles += 2
            # callback gets executed when waiting is done.
            self._waiting_callback = lambda: self._cache.load_from_memory(address)
            print(f"CPU{self._number}: Read {address:018x} -> MISS!")
            return
        
        # READ HIT!
        print(f"CPU{self._number}: Read {address:018x} -> HIT! result: {value:#x} ")
        return value
    
    def _handle_write(self, address, value):
        data = self._cache.write(address, value)
        if data is None:
            # WRITE MISS!

            self.state = CpuState.waiting_for_memory
            self._waiting_cycles += 2
            # callback gets executed when waiting is done. 
            # First load entire cache line into cache, then run cache.write() again to do the update
            self._waiting_callback = lambda: (self._cache.load_from_memory(address), self._cache.write(address, value))
            print(f"CPU{self._number}: Write {address:018x} value {value:#x} -> MISS!")
            return
        
        # WRITE HIT!
        print(f"CPU{self._number}: Write {address:018x} value {value:#x} -> HIT!")
        return