from cache import Cache
from enum import Enum
from memory import Memory
import util

class CpuState(Enum):
    ready = 0
    waiting_for_memory = 1
    finished = 2


class Cpu:
    """Class simulating a CPU/Core that executes memory traces"""

    def __init__(self, number, file_path, cache :Cache):
        self._number = number                           # Number of CPU used for printing
        self._cache = cache
        self._traces_file = open(file_path, 'r')
        self.state = CpuState.ready
        self._waiting_cycles = 0                        # number of remaining cycles to wait

    def handle_next_instruction(self):
        """this function is executed once in every cycle"""

        match self.state:
            case CpuState.finished:
                print(f"CPU{self._number}: No more instructions") 
                return            
            
            case CpuState.waiting_for_memory:
                if self._waiting_cycles > 0:
                    # skip cycle to simulate waiting for memory access
                    self._waiting_cycles -= 1
                    print(f"CPU{self._number}: Waiting for Memory")
                    return
                elif self._waiting_cycles == 0:
                    # finally, the waiting is done :)
                    print(f"CPU{self._number}: Memory access completed")
                    self.state = CpuState.ready
                    return

            case CpuState.ready:
                # read next instruction   
                while True:
                    line = self._traces_file.readline()
                    if not line:
                        print(f"CPU{self._number}: No more instructions") 
                        self.state = CpuState.finished
                        return
                    if line.startswith('#'):
                        # line is commented, read next
                        continue
                    break

                # parse instruction
                parts = line.split()
                command = parts[0]
                
                match command:
                    case 'R':
                        address = int(parts[1], 16)
                        return self._handle_read(address)
                    case 'W':
                        address = int(parts[1], 16)
                        value = int(parts[2], 16)
                        return self._handle_write(address, value)
                    case 'NOP':
                        print(f"CPU{self._number}: NOP")
                        return
    

    def _handle_read(self, address):
        print(f"CPU{self._number}: Read {address:018x}")
        value, hit, memory_access = self._cache.cpu_read(address)
        if hit:
            print(f"CPU{self._number}: Cache Hit! result: {value:#x} ")
        else:
            print(f"CPU{self._number}: Cache Miss!")
            if memory_access:
                print(f"CPU{self._number}: Have to access main memory now :(")
                # skip next few cycles to simulate waiting for memory (even though it is already there)
                # self.state = CpuState.waiting_for_memory
                # self._waiting_cycles += 2
                return
            print(f"CPU{self._number}: Got the value from another cache :) result: {value:#x}")


    def _handle_write(self, address, value):
        print(f"CPU{self._number}: Write {address:018x} value {value:#x}")
        hit, memory_access = self._cache.cpu_write(address, value)
        if hit:
            print(f"CPU{self._number}: Cache Hit! Write Completed")
        else:
            print(f"CPU{self._number}: Cache Miss!")
            if memory_access:
                print(f"CPU{self._number}: Have to access main memory now :(")
                # skip next few cycles to simulate waiting for memory (even though it is already there)
                # self.state = CpuState.waiting_for_memory
                # self._waiting_cycles += 2
                return
            print(f"CPU{self._number}: Got the value from another cache :) Write Completed")