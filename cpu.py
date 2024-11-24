from cache import Cache, PendingTransactionException
from enum import Enum

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
        self._current_instruction = None
        self._retry_last_instruction = False
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
                    # skip cycle
                    self._waiting_cycles -= 1
                    print(f"CPU{self._number}: Waiting for Memory")
                    return
                elif self._waiting_cycles == 0:
                    # waiting is done, cache is ready now
                    self._cache.clear_pending()
                    print(f"CPU{self._number}: Memory access completed")
                    self.state = CpuState.ready
                    return

            case CpuState.ready:
                if self._retry_last_instruction:
                    print(f"CPU{self._number}: Retrying last instruction") 
                    self._retry_last_instruction = False
                else:
                    # read next instruction
                    line = self._traces_file.readline()
                    if not line:
                        print(f"CPU{self._number}: No more instructions") 
                        self.state = CpuState.finished
                        return
                    self._current_instruction = line

                # parse instruction
                parts = self._current_instruction.split()
                match parts[0]:
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
        try:
            value, hit = self._cache.cpu_read(address)
        except PendingTransactionException:
            self._retry_last_instruction = 1
            print(f"CPU{self._number}: Cache Miss!")
            print(f"CPU{self._number}: Resource is blocked by pending instruction. Abort")
            return

        if hit:
            print(f"CPU{self._number}: Cache Hit! result: {value:#x} ")
        else:
            print(f"CPU{self._number}: Cache Miss!")
            if self._cache._pending_line:
                print(f"CPU{self._number}: Waiting for Memory")
                # skip next few cycles to simulate waiting for memory (even though it is already there)
                self.state = CpuState.waiting_for_memory
                self._waiting_cycles += 2
                return
            print(f"CPU{self._number}: Received the block from another cache :) result: {value:#x}")


    def _handle_write(self, address, value):
        print(f"CPU{self._number}: Write {address:018x} value {value:#x}")
        try:
            hit = self._cache.cpu_write(address, value)
        except PendingTransactionException:
            self._retry_last_instruction = 1
            print(f"CPU{self._number}: Cache Miss!")
            print(f"CPU{self._number}: Resource is blocked by pending instruction. Abort")
            return

        if hit:
            print(f"CPU{self._number}: Cache Hit! Write Completed")
        else:
            print(f"CPU{self._number}: Cache Miss!")
            if self._cache._pending_line:
                print(f"CPU{self._number}: Waiting for Memory")
                # skip next few cycles to simulate waiting for memory (even though it is already there)
                self.state = CpuState.waiting_for_memory
                self._waiting_cycles += 2
                return
            print(f"CPU{self._number}: Received the block from another cache :) Write Completed")
