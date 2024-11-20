from memory import Memory
from cache import Cache

block_size = 16

memory = Memory(block_size)
cache = Cache(line_count = 16, block_size = block_size, memory = memory)


cache.read(16)
memory.print()

cache.read(36)
cache.read(38)
cache.read(32)
cache.read(120)

memory.print()

memory.write_byte(29, 0xFF)
memory.write_byte(0xF4, 0xFF)

memory.print()