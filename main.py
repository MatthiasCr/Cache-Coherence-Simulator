from memory import Memory

memory = Memory(16)

memory.print()

memory.read_block(16)
memory.print()

memory.read_block(36)
memory.read_block(120)

memory.print()

print(f"{memory.read(29):02x}")

memory.write(29, 0xFF)
memory.write(0xF4, 0xFF)

memory.print()