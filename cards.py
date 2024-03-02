from dataclasses import dataclass

import database

@dataclass
class Card:
    name: str
    playability: dict[str, float]

def get_card(card: str) -> Card | None:
    rs = database.select('SELECT card, normalized_score, format FROM card_playability WHERE card = ?', [card])
    if not rs:
        return None
    playability = {row['format']: row['normalized_score'] for row in rs}
    return Card(card, playability)

def get_card_names() -> list[dict]:
    return database.values('SELECT DISTINCT card FROM card_playability ORDER BY normalized_score DESC, card', [])

def set_playability() -> None:
    database.execute('''
        CREATE OR REPLACE TABLE card_playability AS
        WITH card_scores AS (
            SELECT
                udc.card,
                e.format,
                LOG(SUM(POWER(3, e.level - 1))) AS raw_score
            FROM
                deck AS d
            INNER JOIN
                event AS e ON d.event_id = e.id
            INNER JOIN
                (
                    SELECT deck_id, card
                    FROM deck_card
                    GROUP BY deck_id, card -- Don't double-count decks where a card is in the maindeck and the sideboard
                ) AS udc ON d.id = udc.deck_id
            WHERE
                e.date > NOW() - INTERVAL 1 YEAR
            GROUP BY
                e.format, udc.card
        ),
        max_scores AS (
            SELECT
                e.format,
                LOG(SUM(POWER(3, e.level - 1))) AS max_score
            FROM
                deck AS d
            INNER JOIN
                event AS e ON d.event_id = e.id
            WHERE
                e.date > NOW() - INTERVAL 1 YEAR
            GROUP BY
                e.format
            HAVING
                max_score > 0
        )
        SELECT
            cs.format,
            cs.card,
            cs.raw_score / ms.max_score AS normalized_score
        FROM
            card_scores AS cs
        INNER JOIN
            max_scores AS ms ON cs.format = ms.format
        ORDER BY
            cs.format, 
            normalized_score DESC,
            cs.card;

    ''', [])
