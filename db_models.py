from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# kreiranje klasa za mapiranje u bazu
class Board(Base):
    __tablename__ = "board"

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self) -> str:
        return f"'Board_ID': '{self.id}', 'Name': '{self.name}', 'Description': '{self.description}'"


class List(Base):
    __tablename__ = "list"

    id = Column(String, primary_key=True)
    name = Column(String)
    board_id = Column(String, ForeignKey("board.id"))

    def __repr__(self) -> str:
        return f"'List_ID': '{self.id}', 'Name': '{self.name}', 'Board_ID': '{self.board_id}'"


class Card(Base):
    __tablename__ = "card"

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    list_id = Column(String, ForeignKey("list.id"))
    board_id = Column(String, ForeignKey("board.id"))

    def __repr__(self) -> str:
        return f"<Card ID: {self.id}, Name: {self.name}, List ID: {self.list_id}, Board ID: {self.board_id}>"


class Checklist(Base):
    __tablename__ = "checklist"

    id = Column(String, primary_key=True)
    name = Column(String)
    card_id = Column(String, ForeignKey("card.id"))
    board_id = Column(String, ForeignKey("board.id"))

    def __repr__(self) -> str:
        return f"<Checklist ID: {self.id}, Name: {self.name}, Card ID: {self.card_id}, Board ID: {self.board_id}>"


class Comment(Base):
    __tablename__ = "comment"

    id = Column(String, primary_key=True)
    text = Column(String)
    full_name = Column(String)
    card_id = Column(String, ForeignKey("card.id"))
    board_id = Column(String, ForeignKey("board.id"))

    def __repr__(self) -> str:
        return f"<Comment ID: {self.id}, Text: {self.text}, Full name: {self.full_name}>, Card ID: {self.card_id}>"


"""class Attachment(Base):
    __tablename__ = "attachment"

    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    card_id = Column(String, ForeignKey("card.id"))

    def __repr__(self) -> str:
        return f"<Attachment ID: {self.id}, Name: {self.name}, Url: {self.url}, Card ID: {self.card_id}>"
"""
