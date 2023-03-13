from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

host = "0.0.0.0"    #   your local address. Enabling local mp 
rooms = {}          #   initialize rooms

challenges = [
    "Give 3 sips",
    "Drink 3 sips",
    "3-2-3-2",
    "Yell Kotler",
    "Yell Kotler",
    "Category",
    "Waterwall",
    "Math game",
    "Make a rule",
    "Question master",
    "Break card",
    "The slave",
    "Story time"
]

def challenge_generator(number):
    return challenges[number-1]


def create_card_deck():
    card_deck = []
    suits = ["clubs", "hearts", "diamonds", "spades"]
    for suit in suits:
        for number in range(1, 14):
            challenge = challenge_generator(number)
            card_deck.append(
                {
                    "name": str(f"{number}-{suit}"),
                    "challenge": str(challenge)
                }
            )
    return card_deck


def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html",
                                   error="Please enter a name.",
                                   code=code, name=name)

        if join is not False and not code:
            return render_template("home.html",
                                   error="Please enter a room code.",
                                   code=code, name=name)

        room = code
        # create new room
        if create is not False:
            # generate new room id and card deck
            room = generate_unique_code(4)
            deck = create_card_deck()
            random.shuffle(deck)
            rooms[room] = {"players": [], "messages": [], "deck": deck, "turn": 0}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")


@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html",
                           code=room,
                           messages=rooms[room]["messages"],
                           deck=rooms[room]["deck"])


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": ""
    }

    #if restart message was received
    if data["data"].startswith("RESTART"):
        #send restart message
        content["message"] = data["data"]
        send(content, to=room)
        rooms[room]["messages"].append(content)
        #send new deck as a message
        new_deck = create_card_deck()
        random.shuffle(new_deck)
        rooms[room]["deck"] = new_deck
        #empty message
        content["message"] = ""
        #add new cards to message as string
        for card in new_deck:
            content["message"] = content["message"] + str(card) + ";"
        #replace ' with "
        content["message"] = content["message"].replace("\'", "\"")
        print(content["message"])
        #send new deck to the room
        send(content, to=room)
    #if message is not restart
    elif data["data"].startswith("Action") or data["data"].startswith("has"):
        content["message"] = data["data"]
        send(content, to=room)
        rooms[room]["messages"].append(content)
        #if message is a card action (not user has left/joined) delete that card from the deck
        if data["data"].startswith("Action"):
            print("Deleting card from deck")
            rooms[room]["deck"].pop()

    print(f"{session.get('name')} sent msg: {data['data']}")

@socketio.on("checkTurn")
def checkTurn():
    room = session.get("room")
    name = session.get("name")
    turn = rooms[room]["turn"]
    players = rooms[room]["players"]

    #If the last player in the list has the turn and they leave, this passes the turn to the first player
    if turn > len(players) - 1:
        rooms[room]["turn"] = 0

    if name == players[turn]:
        if len(players) == turn + 1:
            rooms[room]["turn"] = 0
        else:
            rooms[room]["turn"] += 1
        emit("myTurn")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    
    rooms[room]["players"].append(name)
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        for player in rooms[room]["players"]:
            if player == name:
                rooms[room]["players"].remove(player)
        if len(rooms[room]["players"]) <= 0:
            del rooms[room]

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


if __name__ == "__main__":
    socketio.run(app, host, debug=True)
