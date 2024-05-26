from dataclasses import dataclass


@dataclass
class Comment:
    id: str
    text: str
    fullName: str
    idCard: str
