import json
import sqlalchemy.exc
import API
import db_models
from client import GenericClient
from file_reader import FileReader as File
from models.board import Board
from models.list import List
from models.card import Card
from models.checklist import Checklist
from models.comment import Comment
from db_connection import DBConnection
from db_models import Base
from fastapi import FastAPI

# deklaracija i inicijalizacija varijabli
trello_key = API.trello_key
trello_token = API.trello_token
board_id = "6643823f5fe1c752dfcb9801"
list_id = "66438240fd83e15957862231"
db_url = "sqlite:///trello.db"
cards = []
checklists = []
comments = []
checklist_json = None
comment_json = None


# instanciranje klase sa API parametrima i klase za konekciju sa bazom
client = GenericClient(trello_key, trello_token)
connection = DBConnection(db_url)

# dohvatanje JSON fajlova i dodavanje u klase u models/ direktorijumu
board_json = client.get("boards/" + board_id)
new_board = Board(board_json.get("id"), board_json.get("name"), board_json.get("desc"))


list_json = client.get("lists/" + list_id)
new_list = List(list_json.get("id"), list_json.get("name"), list_json.get("idBoard"))

cards_json = client.get("boards/" + board_id + "/cards")
for card in cards_json:
    cards.append(Card(card.get("id"), card.get("name"), card.get("desc"), card.get("idList"), card.get("idBoard")))
    # kreiranje checklist objekata za svaku karticu
    checklist_json = client.get("cards/" + card.get("id") + "/checklists")
    for checklist in checklist_json:
        checklists.append(Checklist(checklist.get("id"), checklist.get("name"),
                                    checklist.get("idCard"), checklist.get("idBoard")))
    # kreiranje comment objekata za svaku karticu
    comment_json = client.get("cards/" + card.get("id") + "/actions?filter=commentCard")
    for comment in comment_json:
        comments.append(Comment(comment.get("id"), comment['data']['text'],
                                comment['memberCreator']['fullName'], comment['data']['card']['id'],
                                comment['data']['board']['id']))


# dodavanje elemenata iz dataclass-a u bazu podataka

Base.metadata.create_all(connection.engine)

db_board = db_models.Board(id=new_board.id, name=new_board.name, description=new_board.desc)
connection.create(db_board)

db_list = db_models.List(id=new_list.id, name=new_list.name, board_id=new_list.idBoard)
connection.create(db_list)

for card in cards:
    new_card = db_models.Card(id=card.id, name=card.name, description=card.desc,
                              list_id=card.idList, board_id=card.idBoard)
    connection.create(new_card)

for checklist in checklists:
    new_checklist = db_models.Checklist(id=checklist.id, name=checklist.name,
                                        card_id=checklist.idCard, board_id=checklist.idBoard)
    connection.create(new_checklist)

for comment in comments:
    new_comment = db_models.Comment(id=comment.id, text=comment.text,
                                    full_name=comment.fullName, card_id=comment.idCard, board_id=comment.idBoard)
    connection.create(new_comment)

""" FAST API """

app = FastAPI()


@app.get("/")
async def root():
    return "Index"


# vraca sve informacije o board-u
@app.get("/boards/{id_board}")
async def get_board(id_board):
    board_ = connection.read(db_models.Board, id=id_board)
    list_ = connection.read(db_models.List, board_id=id_board)
    card_ = connection.read(db_models.Card, board_id=id_board)
    checklist_ = connection.read(db_models.Checklist, board_id=id_board)
    comment_ = connection.read(db_models.Comment, board_id=id_board)
    return board_ + list_ + card_ + checklist_ + comment_


# vracanje informacije o listi i njenim karticama
@app.get("/lists/{id_list}")
async def get_list(id_list):
    list_ = connection.read(db_models.List, id=id_list)
    card_ = connection.read(db_models.Card, list_id=id_list)
    return list_ + card_


# vracanje informacije o kartici i njenim checklista-ma i komentarima
@app.get("/cards/{id_card}")
async def get_cards(id_card):
    card_ = connection.read(db_models.Card, id=id_card)
    checklist_ = connection.read(db_models.Checklist, card_id=id_card)
    comment_ = connection.read(db_models.Comment, card_id=id_card)
    return card_ + checklist_ + comment_


# pravljenje nove kartice na trello listi i dodavanje u bazu
@app.post("/card")
async def create_card(card_: Card):
    try:
        post_request = client.post("cards", idList=card_.idList, name=card_.name, desc=card_.desc)
        new_id = post_request.get("id")
        new_board_id = post_request.get("idBoard")
        new_card_ = db_models.Card(id=new_id, name=card_.name, description=card_.desc,
                                   list_id=card_.idList, board_id=new_board_id)
        return connection.create(new_card_) + json.dumps(post_request)
    except sqlalchemy.exc.IntegrityError as ie:
        return "Card with the same ID already exists: " + ie.__repr__()
    except sqlalchemy.exc.InvalidRequestError as ir:
        return "Error: " + ir.__repr__()


# pravljenje nove liste na trello board i dodavanje u bazu
@app.post("/list")
async def create_list(list_: List):
    try:
        post_request = client.post("lists", idBoard=list_.idBoard, name=list_.name)
        new_id = post_request.get("id")
        new_list_ = db_models.List(id=new_id, name=list_.name, board_id=list_.idBoard)
        return connection.create(new_list_) + json.dumps(post_request)
    except sqlalchemy.exc.IntegrityError as ie:
        return "List with the same ID already exists: " + ie.__repr__()
    except sqlalchemy.exc.InvalidRequestError as ir:
        return "Error: " + ir.__repr__()


# brisanje kartice sa trello liste i iz baze
@app.delete("/delete_card")
async def delete_card(id_card: str):
    try:
        delete_request = client.delete("cards/" + id_card)
        return connection.delete(db_models.Card, id=id_card) + json.dumps(delete_request)
    except sqlalchemy.exc.DataError as de:
        return "Error: " + de.__repr__()
    except sqlalchemy.exc.InvalidRequestError as ir:
        return "Error: " + ir.__repr__()


# azuriranje imena liste i promena u bazi
@app.put("/update_list")
async def update_list(id_list: str, name: str):
    try:
        put_request = client.put("lists/" + id_list, name=name)
        return connection.update(db_models.List, name, id=id_list) + json.dumps(put_request)
    except sqlalchemy.exc.DataError as de:
        return "Error: " + de.__repr__()
    except sqlalchemy.exc.InvalidRequestError as ir:
        return "Error: " + ir.__repr__()

"""
file_directory = File("files/")

# stampanje klasa iz models/ direktorijuma
print(new_board.__str__() + "\n")
print(new_list.__str__() + "\n")
for card in cards:
    print(card.__str__())
    for checklist in checklists:
        if checklist.idCard == card.id:
            print("    " + checklist.__str__())
    for comment in comments:
        if comment.idCard == card.id:
            print("    " + comment.__str__())
print("")

# cuvanje fajlova u files/ direktorijum
file_directory.save_file("board.json", board_json)
file_directory.save_file("list.json", list_json)
file_directory.save_file("cards.json", cards_json)
file_directory.save_file("comments.json", comment_json)

# dohvatanje i cuvanje attachmenta
for card in cards:
    try:
        attachment_json = client.get("cards/" + card.id + "/attachments")
        att_url = attachment_json[0]["url"]
        att_name = attachment_json[0]["fileName"]
        att_id = attachment_json[0]["id"]
        file_directory.download_attachment(att_id + "_", att_name, att_url)
    except IndexError as ie:
        print("No attachments for card id: " + card.id)

# prikazivanje svih fajlova u direktorijumu
print("\nAll files in /" + file_directory.directory + " directory:")
file_directory.all_files()

# prikazivanje detalja svih fajlova
print("\nAll files with details:\n")
file_directory.print_all()
"""