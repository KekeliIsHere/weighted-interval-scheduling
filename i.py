class Request:
    id: int
    start: int
    finish: int
    value: int
    
    def __init__(self, id, start, finish, value):
        self.id = id
        self.start = start
        self.finish = finish
        self.value = value

        if self.start >= self.finish:
            raise ValueError("Start must be < finish")
        if self.value <= 0:
            raise ValueError("Value must be positive")

    def compatible_with(self, other):
        return self.finish <= other.start or other.finish <= self.start