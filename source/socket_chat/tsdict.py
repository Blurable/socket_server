import threading


class ThreadSafeDict:
    def __init__(self):
        self.dictionary = {}
        self.lock = threading.Lock()


    def __delitem__(self, key):
        with self.lock:
            if key in self.dictionary:
                del self.dictionary[key]

    
    def __contains__(self, key):
        with self.lock:
            return True if key in self.dictionary else False
    

    def copy_values(self):
        with self.lock:
            return list(self.dictionary.values())
        

    def copy_keys(self):
        with self.lock:
            return list(self.dictionary.keys())
        

    def add_if_not_exists(self, key, value):
        with self.lock:
            if key not in self.dictionary:
                self.dictionary[key] = value
                return True
            return False
        
        
    def get_if_exists(self, key):
        with self.lock:
            if key in self.dictionary:
                return self.dictionary[key]
            return None
        

    def __repr__(self):
        return f"CustomDict({self.dictionary})"


    def __str__(self):
        return str(self.dictionary)