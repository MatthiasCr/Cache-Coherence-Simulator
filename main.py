from src.bus import Bus
from src.cpu import Cpu, CpuState
from src.cache import Cache
from src.memory import Memory
from pathlib import Path


block_size = 8
line_count = 3

base_dir = Path(__file__)
memory_traces_1 = base_dir / '..' / 'memory_traces' / 'traces_cpu1.txt'
memory_traces_2 = base_dir / '..' / 'memory_traces' / 'traces_cpu2.txt'


# initialize components
memory = Memory(block_size)
bus = Bus()

cache1 = Cache(1, line_count, block_size, bus)
cpu1 = Cpu(1, memory_traces_1.resolve(), cache1)

cache2 = Cache(2, line_count, block_size, bus)
cpu2 = Cpu(2, memory_traces_2.resolve(), cache2)

bus.connect_memory(memory)
bus.connect_cache(cache1)
bus.connect_cache(cache2)


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
            case "help":
                print_help()
            case _:
                print("Unknown command")
        handle_user_input()
    except KeyboardInterrupt:
        exit()

def print_help():
    print(f"Using {block_size} bytes block size and {line_count} lines per cache")
    print("Press ENTER to step to next cycle")
    print("Type c1 or c2 to print caches")
    print("Type mem to print memory")


# 
# Main Program Loop
# 
print_help()
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
while True:
    handle_user_input()
