from typing import List


def props(cls: object) -> List[str]:
    return [i for i in cls.__dict__.keys() if i[:1] != '_']
