from memory import Memory
from cache import Cache

block_size = 16

memory = Memory(block_size)
cache = Cache(line_count = 4, block_size = block_size, memory = memory)

cache.read(16)
# cache.print()

cache.read(36)
# cache.print()

cache.read(38)
# cache.print()

cache.read(32)
# cache.print()
cache.read(120)
# cache.print()

cache.write(32, 0xF4)
# cache.print()

cache.write(0xF310309, 0x44)
# cache.print()

cache.read(17)
cache.print()


# cache.write(0xFFFF, 0x42)

#memory.write_byte(29, 0xFF)
#memory.write_byte(0xF4, 0xFF)

