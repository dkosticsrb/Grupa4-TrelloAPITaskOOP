import API
from models.board import Board
from models.list import List
from models.card import Card
from models.checklist import Checklist
from models.comment import Comment
from client import GenericClient
from file_reader import FileReader as File

# deklaracija i inicijalizacija varijabli
trello_key = API.trello_key
trello_token = API.trello_token
board_id = "6643823f5fe1c752dfcb9801"
list_id = "66438240fd83e15957862231"
cards = []
checklists = []
comments = []
checklist_json = None
comment_json = None

# instanciranje klase sa API parametrima i klase sa putanjom do direktorijuma
client = GenericClient(trello_key, trello_token)
file_directory = File("files/")

# dohvatanje JSON fajlova i dodavanje u klase u models/ direktorijumu
board_json = client.get("boards/" + board_id)
new_board = Board(board_json.get("id"), board_json.get("name"), board_json.get("desc"))

list_json = client.get("lists/" + list_id)
new_list = List(list_json.get("id"), list_json.get("name"), list_json.get("idBoard"))

cards_json = client.get("boards/" + board_id + "/cards")
for card in cards_json:
    cards.append(Card(card.get("id"), card.get("name"), card.get("desc")))
    # kreiranje checklist objekata za svaku karticu
    checklist_json = client.get("cards/" + card.get("id") + "/checklists")
    for checklist in checklist_json:
        new_checklist = Checklist(
            checklist.get("id"),
            checklist.get("name"),
            checklist.get("idBoard"),
            checklist.get("idCard")
        )
        checklists.append(new_checklist)
    # kreiranje comment objekata za svaku karticu
    comment_json = client.get("cards/" + card.get("id") + "/actions?filter=commentCard")
    for comment in comment_json:
        new_comment = Comment(
            comment.get("id"),
            comment['data']['text'],
            comment['memberCreator']['fullName'],
            comment['data']['card']['id']
        )
        comments.append(new_comment)

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
    except IndexError:
        print("No attachments for card id: " + card.id)

# prikazivanje svih fajlova u direktorijumu
print("\nAll files in /" + file_directory.directory + " directory:")
file_directory.all_files()

# prikazivanje detalja svih fajlova
print("\nAll files with details:\n")
file_directory.print_all()
