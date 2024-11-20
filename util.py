def is_valid_address(address):
    """checks if address is 64 bit integer"""
    if not isinstance(address, int):
        return False
    return 0 <= address < (1 << 64)