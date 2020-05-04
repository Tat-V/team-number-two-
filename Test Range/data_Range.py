class DataRange(object):
    def __init__(self):
        self.my_range = None

    def generate(self, i):
        self.my_range = range(i)

    def get_range(self):
        return self.my_range
