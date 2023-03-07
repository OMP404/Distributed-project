from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

rooms = {}



def challenge_generator(number):
    if number == 1:
        challenge = "Give 3 sips"
    if number == 2:
        challenge = "Drink 3 sips"
    if number == 3:
        challenge = "3-2-3-2"
    if number == 4:
        challenge = "Yell Kotler"
    if number == 5:
        challenge = "Yell Kotler"
    if number == 6:
        challenge = "Category"
    if number == 7:
        challenge = "Waterwall"
    if number == 8:
        challenge = "Math game"
    if number == 9:
        challenge = "Make a rule"
    if number == 10:
        challenge = "Question master"
    if number == 11:
        challenge = "Break card"
    if number == 12:
        challenge = "The bitch"
    if number == 13:
        challenge = "Story time"
    
    return challenge

#testing stuff
def create_card_deck():
    card_deck = []
    suits = ["clubs", "hearts", "diamonds", "spades"]
    for suit in suits:
        for number in range(1,14):
            challenge = challenge_generator(number)
            card_deck.append(
                {
                    "name": str("{}-{}".format(number, suit)),
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
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        #create new room
        if create != False:
            #generate new room id and card deck
            room = generate_unique_code(4)
            deck = create_card_deck()
            random.shuffle(deck)
            rooms[room] = {"members": 0, "messages": [], "deck": deck}
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

    return render_template("room.html", code=room, messages=rooms[room]["messages"], deck=rooms[room]["deck"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    #if message is a card action (not user has left/joined) delete that card from the deck
    if not data["data"].startswith("has"):
        print("Deleting card from deck")
        rooms[room]["deck"].pop()

    print(f"{session.get('name')} said: {data['data']}")


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
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)