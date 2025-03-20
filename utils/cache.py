from collections import OrderedDict

class ImageCache:
    def __init__(self, max_size=50):
        self.cache = OrderedDict()
        self.max_size = max_size

    def add(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get(self, key):
        return self.cache.get(key, None)

    def has(self, key):
        """Clearly checks if a key is already cached."""
        return key in self.cache

    def evict(self, keys):
        """Evicts multiple keys clearly and efficiently."""
        for key in keys:
            self.cache.pop(key, None)
