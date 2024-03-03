import json

import cards
import database


def load() -> None:
    card_names = cards.get_card_names()
    f = open("data/carddict.json", "r")
    s = f.read()
    d = json.loads(s)
    max_popularity = max(card["popularity"] for card in d.values())
    max_elo = max(card["elo"] for card in d.values())
    database.execute("DELETE FROM cube", [])
    cube_sql = "INSERT IGNORE INTO cube (card, popularity, elo) VALUES (?, ?, ?)"
    popularity_sql = "INSERT INTO card_playability (card, format, normalized_score) VALUES (?, 'CPOP', ?) ON DUPLICATE KEY UPDATE normalized_score = ?"
    elo_sql = "INSERT INTO card_playability (card, format, normalized_score) VALUES (?, 'CELO', ?) ON DUPLICATE KEY UPDATE normalized_score = ?"
    for _scryfall_id, card in d.items():
        if card["name"] in card_names:  # Skip art cards and tokens, etc.
            database.insert(cube_sql, [card["name"], card["popularity"], card["elo"]])
            normalized_popularity = card["popularity"] / max_popularity
            database.insert(popularity_sql, [card["name"], normalized_popularity, normalized_popularity])
            normalized_elo = card["elo"] / max_elo
            database.insert(elo_sql, [card["name"], normalized_elo, normalized_elo])
