from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from http import HTTPMethod
from time import sleep
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
import requests

import database

class Level(Enum):
    PROFESSIONAL = 4
    MAJOR = 3
    COMPETITIVE = 2
    REGULAR = 1

class Format(Enum):
    VINTAGE = 'VI'
    LEGACY = 'LE'
    MODERN = 'MO'
    PIONEER = 'PI'
    EXTENDED = 'EX'
    HISTORIC = 'HI'
    STANDARD = 'ST'
    BLOCK = 'BL'
    PAUPER = 'PAU'
    CEDH = 'cEDH'
    DUEL_COMMANDER = 'EDH'
    MTGO_COMMANDER = 'EDHM'
    EXPLORER = 'EXP'
    HIGHLANDER = 'HIGH'
    CANADIAN_HIGHLANDER = 'CHL'
    PEASANT = 'PEA'
    ALCHEMY = 'ALCH'
    PREMODERN = 'PREM'
    LIMITED = 'LI'

@dataclass
class Rank:
    high: int | None
    low: int | None

@dataclass
class Row:
    deck_name: str
    deck_id: int
    player: str
    format: Format
    event_name: str
    event_id: int
    level: Level
    rank: Rank | None
    date: datetime

@dataclass
class Event:
    id: int
    name: str
    format: Format
    url: str
    level: Level
    num_players: int | None
    date: datetime

@dataclass
class Entry:
    card: str
    num: int
    sideboard: bool

@dataclass
class Deck:
    id: int
    name: str
    player: str
    event_id: int
    rank: Rank
    decklist: list[Entry]

class InvalidHTTPMethod(Exception):
    pass

def main() -> None:
    page = 1
    while True:
        rows = search(page)
        for row in rows:
            event = load_or_fetch_event(row.event_id, row.event_name, row.format)
            load_or_fetch_deck(row.deck_id, row.deck_name, row.player, event.id, row.rank)
        page += 1

def search(page: int) -> list[Row]:
    s = fetch(HTTPMethod.POST, '/search', {'current_page': page})
    return parse_search(s)

def parse_search(s: str) -> list[Row]:
    soup = BeautifulSoup(s, 'html.parser')
    # <form method=POST action=compare name=compare_decks>
    form = soup.find('form', {'name': 'compare_decks'})
    trs = form.find_all('tr', {'class': 'hover_tr'})[1:] # First row is the header
    rows = []
    for tr in trs:
        tds = tr.find_all('td')
        #     <td class=S12>
        #         <a href=event?e= 52695&d=591521&f= PI>Amalia Life</a>
        #     </td>
        deck_name = tds[1].a.string or ""
        parsed_url = urlparse(tds[1].a['href'])
        qs = parse_qs(parsed_url.query)
        deck_id = int(qs.get('d')[0])
        event_id = int(qs.get('e')[0])
        format = Format(qs.get('f')[0])
        #     <td class=G12>
        #         <a class=player href=search?player= Josh+Bradbury>Josh Bradbury</a>
        #     </td>
        player = tds[2].a.string or ""
        #     <td class=S11>
        #         <a href=event?e= 52695&f=PI>2nd Chance PTQ @ MagicCon : Chicago</a>
        #     </td>
        event_name = tds[4].a.string
        #     <td align=center>
        #         <img src=/graph/star.png>
        #         <img src=/graph/star.png>
        #         <img src=/graph/star.png>
        #     </td>
        level = parse_level(tds[5])
        #     <td class=S12 align=center>17-32</td>
        rank = parse_rank(tds[6].string)
        #     <td class=S11>25/02/24</td>
        date = datetime.strptime(tds[7].string, '%d/%m/%y')
        row = Row(deck_name, deck_id, player, format, event_name, event_id, level, rank, date)
        rows.append(row)
    return rows

def parse_level(elem) -> Level:
    if 'bigstar' in str(elem):
        return Level.PROFESSIONAL
    return Level(len(elem.find_all('img')))  # 1, 2 or 3 star images for the three lower levels

def parse_rank(rank: str) -> Rank | None:
    if not rank:
        return Rank(None, None)
    try:
        if '-' not in rank:
            return Rank(int(rank), int(rank))
        parts = rank.split('-')
        return Rank(int(parts[1]), int(parts[0]))
    except ValueError:
        print("We saw a rank we didn't understand:", rank)
        return Rank(None, None)

def load_or_fetch_event(event_id: int, event_name: str, format: Format) -> Event:
    event = load_event(event_id)
    if event:
        return event
    return fetch_event(event_id, event_name, format)

def load_event(event_id: int) -> Event | None:
    result = database.select('SELECT id, name, format, url, level, num_players, date FROM event WHERE id = ?', [event_id])
    return Event(*result[0]) if result else None

def fetch_event(event_id: int, event_name: str, format: Format) -> Event:
    s = fetch(HTTPMethod.GET, f'/event?e={event_id}')
    event = parse_event(event_id, event_name, format, s)
    return store_event(event)

def parse_event(event_id: int, event_name: str, format: Format, s: str) -> Event:
    soup = BeautifulSoup(s, 'html.parser')
    # <div class="S14" align="center" style="background:white;margin-bottom:4px;">
    info = soup.find('div', {'class': 'S14'})
    divs = info.find_all('div')
    # 	<div class="meta_arch" style="padding:2px;">Pioneer <img src="/graph/bigstar.png" height="20"></div>
    level = parse_level(divs[0])
    # 	<div style="margin-bottom:5px;">257 players - 23/02/24</div>
    print(divs[1].string)
    if ' - ' in divs[1].string:
        parts = divs[1].string.split(' - ')
        num_players = int(parts[0].replace(' players', ''))
        date_s = parts[1]
    else:
        num_players = None
        date_s = divs[1].string
    date = datetime.strptime(date_s, '%d/%m/%y')
    # 	<div class="S10" style="width:250px;overflow:hidden;padding-bottom:5px;"><div class="S10" style="width:250px;overflow:hidden;padding-bottom:5px;">Source: <a target="_blank" href="https://magic.gg/events/pro-tour-murders-at-karlov-manor">magic.gg</a></div></div>
    try:
        url = divs[2].a['href']
    except TypeError:
        url = None
    # </div>
    return Event(event_id, event_name, format, url, level, num_players, date)

def store_event(event: Event) -> Event:
    database.insert('INSERT INTO event (id, name, date, format, level, url, num_players) VALUES (?, ?, ?, ?, ?, ?, ?)', [event.id, event.name, event.date, event.format.value, event.level.value, event.url, event.num_players])
    return load_event(event.id)

def load_or_fetch_deck(deck_id: int, deck_name: str, player: str, event_id: int, rank: Rank) -> None:
    if not database.select('SELECT id FROM deck WHERE id = ?', [deck_id]):
        deck = Deck(deck_id, deck_name, player, event_id, rank, [])
        deck.decklist = fetch_decklist(deck_id)
        store_deck(deck)

def fetch_decklist(deck_id: int) -> list[Entry]:
    s = fetch(HTTPMethod.GET, f'/mtgo?d={deck_id}')
    return parse_decklist(s)

def parse_decklist(s: str) -> list[Entry]:
    sideboard, decklist = False, []
    lines = s.split('\r\n')
    for line in lines:
        if line == 'Sideboard':
            sideboard = True
            continue
        if not line:
            continue
        parts = line.split(' ', 1)
        n = int(parts[0])
        card = parts[1]
        decklist.append(Entry(card, n, sideboard))
    return decklist

def store_deck(deck: Deck) -> None:
    database.insert('INSERT INTO deck (id, name, player, event_id, rank_high, rank_low) VALUES (?, ?, ?, ?, ?, ?)', [deck.id, deck.name, deck.player, deck.event_id, deck.rank.high, deck.rank.low])
    for entry in deck.decklist:
        database.insert('INSERT INTO deck_card (deck_id, card, num, sideboard) VALUES (?, ?, ?, ?)', [deck.id, entry.card, entry.num, entry.sideboard])

def fetch(method: HTTPMethod, path: str, data: dict | None = None, failures: int = 0) -> str:
    s = f'Fetching {method} {path}'
    if data:
        s += f' with {data}'
    print(s)
    sleep(0.1)
    try:
        response = requests.request(method, f'https://www.mtgtop8.com{path}', data=data)
    except ConnectionError:
        print(f"Connection error. {failures} failures so far.")
        if failures > 2:
            raise
        sleep(5)
        return fetch(method, path, data, failures + 1)
    return response.text

main()
