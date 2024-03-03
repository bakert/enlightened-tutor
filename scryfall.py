import json

import requests

import database


def import_cards():
    response = requests.get("https://api.scryfall.com/catalog/card-names")
    d = json.loads(response.text)
    cards = d["data"]
    database.execute("DELETE FROM card", [])
    for card in cards:
        sql = "INSERT INTO card (name) VALUES (?)"
        database.execute(sql, [card])
    return len(cards)
