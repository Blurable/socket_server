import threading
from collections import UserDict
from typing import Any


class ThreadSafeDict(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def __getitem__(self, key: Any) -> Any:
        with self.lock:
            return super().__getitem__(key)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        with self.lock:
            super().__setitem__(key, value)
        
    def __delitem__(self, key: Any) -> None:
        with self.lock:
            if key in self.data:
                super().__delitem__(key)

    def __contains__(self, key):
        with self.lock:
            return super().__contains__(key)
    
    def copy_keys(self):
        with self.lock:
            return list(self.data.keys())
    
    def copy_values(self):
        with self.lock:
            return list(self.data.values())    
        
    def add_if_not_exists(self, key, value):
        with self.lock:
            if key not in self.data:
                super().__setitem__(key, value)
                return True
            return False
        
    def get_if_exists(self, key):
        with self.lock:
            if key in self.data:
                return super().__getitem__(key)
            return None