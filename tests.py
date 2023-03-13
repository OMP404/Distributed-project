import pytest
from main import app, rooms, generate_unique_code, create_card_deck


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_homepage_post(client):
    response = client.post(
        "/", data=dict(name="test", code="", join=False, create=False))
    assert response.status_code == 200
    assert b"Please enter a room code." in response.data


def test_create_room(client):
    response = client.post(
        "/", data=dict(name="test", code="", join=False, create=True))
    assert response.status_code == 200


def test_room(client):
    with client.session_transaction() as session:
        session["room"] = "TEST"
        session["name"] = "test"

    rooms["TEST"] = {
        "players": [{"name": "test", "turn": 0}],
        "messages": [{"name": "test", "message": "has entered the room"}],
        "deck": create_card_deck()
    }

    response = client.get("/room")
    assert response.status_code == 200
    assert b"TEST" in response.data


def test_generate_unique_code():
    code1 = generate_unique_code(4)
    code2 = generate_unique_code(4)
    assert len(code1) == 4
    assert code1 != code2


def test_create_card_deck():
    deck = create_card_deck()
    assert len(deck) == 52
    assert deck[0]['name'] == '1-clubs'
    assert deck[0]['challenge'] == 'Give 3 sips'
    assert deck[-1]['name'] == '13-spades'
    assert deck[-1]['challenge'] == 'Story time'
