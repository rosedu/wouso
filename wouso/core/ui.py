
class BlockLibrary(object):
    def __init__(self):
        self.parts = {}

    def get_blocks(self):
        return self.parts.keys()

    def get_block(self, key, context):
        block = self.parts.get(key, '')
        if callable(block):
            return block(context)
        return block

    def add(self, key, callback):
        self.parts[key] = callback

_block_library = None
def get_sidebar():
    global _block_library
    if _block_library is None:
        _block_library = BlockLibrary()
    return _block_library

def register_sidebar_block(name, callback):
    lib = get_sidebar()
    lib.add(name, callback)
