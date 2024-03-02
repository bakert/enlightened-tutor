# enlightened-tutor
Program that checks Magic: the Gathering cards for tournament playability and other interesting facets

MIT License

(c) 2024 Thomas David Baker <bakert@gmail.com>

## Setup
- Install Python
- $ git clone https://github.com/bakert/enlightened-tutor
- $ cd enlightened-tutor
- $ python3 -m venv .
- $ source bin/activate
- $ pip install -r requirements.txt
- Install mariadb
- $ mysql
- mysql> CREATE USER 'enlightened_tutor'@'localhost' IDENTIFIED BY 'YOUR-PASSWORD-HERE';
- mysql> GRANT ALL ON enlightened_tutor.* TO 'enlightened_tutor'@'localhost';
- Run the SQL in enlightened-tutor.sql
- Copy config.ini.example to config.ini and fill in the database information

### Web Server
- $ bin/uvicorn web:app --reload --log-level info --port 8000
(Note: this will not give interesting results until the database is populated)

### Tournament Decklist Scraper
- Restore latest file in data/ to avoid hours of requests
- $ python3 mtgtop8.py # You can kill this once it starts seeing decks you already have
- $ python3 -c "import cards; cards.set_playability()"
