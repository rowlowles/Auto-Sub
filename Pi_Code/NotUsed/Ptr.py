# This class simulates C/C++ pointers

class ptr(object):
    def __init__(self, value=None):
        self._x = value
    def get(self):
        return self._x
    def set(self, value):
        self._x = value
    x = property(get, set)