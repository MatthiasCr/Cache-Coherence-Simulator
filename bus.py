from memory import Memory
from enum import Enum

class BusMessageType(Enum):
    read = 0     # read from main memory OR from other cache if available (cache-to-cache transfer)
    write = 1    # write to main memory
    read_w = 2   # "read with intent to write". That means a write miss just happened and cpu needs to read before write
    upgr = 3     # "upgrade privileges". A cache has a shared block, but now wants exclusive rights to write on it 

class BusMessage:
    def __init__(self, type :BusMessageType, block, value = None):
        self.type = type
        self.block = block
        self.value = value      # In case of a write message
        return


class Bus:
    def __init__(self):
        self._caches = []       # Array of all caches connected to bus
        self._memory :Memory = None
        return
    
    # initialization
    def connect_cache(self, cache):
        self._caches.append(cache)

    def connect_memory(self, memory):
        self._memory = memory
    

    def put_message(self, sender, message :BusMessage):
        """returns tuple of requested data and a boolean that specifies if main memory was accessed or not"""

        # first broadcast message to all connected caches so they can snoop it and maybe respond
        data = self._notify_listeners(sender, message)

        match message.type:
            case BusMessageType.read | BusMessageType.read_w:
                memory_access = False
                if not data:
                    # no other cache has requested value, need to access main memory
                    memory_access = True
                    data = self._memory.read_block(message.block)
                return data, memory_access

            case BusMessageType.write:
                self._memory.write_block(message.block, message.value)
                return None, True
            
            case BusMessageType.upgr:
                # this message type only has the purpose to inform other caches, no need to do anything else
                return None, False


    def _notify_listeners(self, sender, message :BusMessage):
        response = None
        for cache in self._caches:
            if cache == sender:
                continue
            res = cache.react_to_bus(message)
            if res:
                response = res
        return response