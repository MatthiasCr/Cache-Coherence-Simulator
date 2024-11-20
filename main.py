from cpu import Cpu, CpuState
from cache import Cache
from memory import Memory

block_size = 16
line_count = 4
memory_traces_file = 'memory_traces/man_cpu1'

memory = Memory(block_size)
cache = Cache(line_count, block_size, memory)
cpu = Cpu(1, memory_traces_file, cache, memory)

def handle_user_input():
    user_input = input(">").strip()
    if user_input == "":
        # user pressed enter -> execute next cycle
        return
    else:
        if user_input.lower() == "exit":
            print("Exiting program.")
            exit()
        elif user_input.lower() == "cache":
            cache.print()
        elif user_input.lower() == "mem":
            memory.print()
        else:
            print("Unknown command")
    handle_user_input()

# 
# Main Program Loop
# 
while not cpu.state == CpuState.finished:
    handle_user_input()
    cpu.handle_next_instruction()

    # cpu2.handle_next_instruction()
    # handle_user_input()

print("All cores finished!")
exit()
