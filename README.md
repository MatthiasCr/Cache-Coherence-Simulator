This was an exercise as part of the lecture "Large Scale Systems Architecture" at HPI.

## About

This command line simulator simulates two cores with own caches executing memory traces. The caches are **fully associative** and **write-back**. Furthermore, they use **least recently used (LRU)** as replacement strategy. For cache coherence this simulator implements the [MESI](https://de.wikipedia.org/wiki/MESI) protocol that is **write-invalidate** and based on a snooping bus.

## Usage

The simulator executes memory traces for both cores. Possible operations include reading and writing single bytes. They should have the following format with addresses and value in hexadecimal:

```
R [addr]            # read byte at [addr] 
W [addr] [value]    # write byte [value] to [addr]
NOP                 # stall for this cycle
```

Start the simulator by running `main.py`.

The simulator runs interactively and executes one cycle at a time. Press `Enter` to proceed to the next cylce. For simplicity, the cores run in alternating cycles, so that only one of the cores performs an operation in each cycle. Furthermore, assumptions are:

- **Cache Hit**: Operation is completed in one cycle

- **Cache Miss**: Core is stalled for three cycles waiting for memory until operation is completed

Between cycles the user can print out the current content of the caches and memory by typing:

`memory` or `mem`

`cache1` or `c1`

`cache2` or `c2`




