from cpu import Cpu, CpuState
from cache import Cache
from memory import Memory

block_size = 16
line_count = 4
memory_traces_1 = 'memory_traces/man_cpu1'
# memory_traces_2 = 'memory_traces/man_cpu2'

# initialize components
memory = Memory(block_size)

cache1 = Cache(line_count, block_size, memory)
cpu1 = Cpu(1, memory_traces_1, cache1, memory)

# cache2 = Cache(line_count, block_size, memory)
# cpu2 = Cpu(1, memory_traces_2, cache2, memory)

def handle_user_input():
    try:
        user_input = input(">").strip()
        if user_input == "":
            # user pressed enter -> execute next cycle
            return
        else:
            if user_input.lower() == "exit":
                print("Exiting program.")
                exit()
            elif user_input.lower() == "cache1":
                cache1.print()
            elif user_input.lower() == "mem":
                memory.print()
            else:
                print("Unknown command")
        handle_user_input()
    except KeyboardInterrupt:
        print("\nAborting")
        exit() 

# 
# Main Program Loop
# 
while not cpu1.state == CpuState.finished: #and not cpu2.state == CpuState.finished
    handle_user_input()
    cpu1.handle_next_instruction()

    # handle_user_input()
    # cpu2.handle_next_instruction()

print("All cores finished!")
exit()
