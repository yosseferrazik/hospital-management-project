from datetime import datetime, timedelta

class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def set(self, key, value, ttl=3600):
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
    
    def get(self, key):
        if key in self._cache:
            if datetime.now() < self._expiry[key]:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._expiry[key]
        return None
    
    def delete(self, key):
        if key in self._cache:
            del self._cache[key]
            del self._expiry[key]
    
    def invalidate(self):
        self._cache.clear()
        self._expiry.clear()
    
    def size(self):
        self._clean_expired()
        return len(self._cache)
    
    def _clean_expired(self):
        now = datetime.now()
        expired = [k for k, v in self._expiry.items() if now >= v]
        for k in expired:
            self.delete(k)

cache = SimpleCache()