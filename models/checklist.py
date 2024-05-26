from dataclasses import dataclass


@dataclass
class Checklist:
    id: str
    name: str
    idBoard: str
    idCard: str
