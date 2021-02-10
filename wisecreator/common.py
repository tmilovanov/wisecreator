from dataclasses import dataclass

class WiseException(Exception):
    def __init__(self, message, desc):
        super().__init__(message)

        self.desc = desc

@dataclass
class Gloss:
    offset: int
    word: str