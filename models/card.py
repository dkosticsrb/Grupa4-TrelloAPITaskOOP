from dataclasses import dataclass


@dataclass
class Card:
    id: str
    name: str
    desc: str
    idList: str
    idBoard: str
