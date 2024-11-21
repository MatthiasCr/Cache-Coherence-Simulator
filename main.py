from cpu import Cpu, CpuState
from cache import Cache
from memory import Memory

block_size = 16
line_count = 4
memory_traces_1 = 'memory_traces/man_cpu1.txt'
memory_traces_2 = 'memory_traces/man_cpu2.txt'

# initialize components
memory = Memory(block_size)

cache1 = Cache(1, line_count, block_size, memory)
cpu1 = Cpu(1, memory_traces_1, cache1)

cache2 = Cache(2, line_count, block_size, memory)
cpu2 = Cpu(2, memory_traces_2, cache2)


def handle_user_input():
    try:
        user_input = input(">").strip()
        match user_input.lower():
            case "":
                # user pressed enter -> execute next cycle
                return
            case "exit":
                exit()
            case "cache1" | "c1":
                cache1.print()
            case "cache2" | "c2":
                cache2.print()
            case "memory" | "mem":
                memory.print()
            case _:
                print("Unknown command")
        handle_user_input()
    except KeyboardInterrupt:
        exit()

# 
# Main Program Loop
# 
while True:
    # each loop iteration represents 2 cycles
    # the cores operate in alternative cycles
    
    handle_user_input()
    cpu1.handle_next_instruction()

    handle_user_input()
    cpu2.handle_next_instruction()

    if cpu1.state == CpuState.finished and cpu2.state == CpuState.finished:
        break

print("All cores finished!")
exit()
