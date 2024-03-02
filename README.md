# enlightened-tutor
Program that checks Magic: the Gathering cards for tournament playability and other interesting facets

MIT License

(c) 2024 Thomas David Baker <bakert@gmail.com>

## Dev Env Setup
1. Install Python
2. Install pip
3. Clone the repo
4. $ python3 -m venv .
5. $ source bin/activate
6. $ pip install -r requirements.txt
7. Install mariadb
8. mysql> CREATE USER 'enlightened_tutor'@'localhost' IDENTIFIED BY 'YOUR-PASSWORD-HERE';
   mysql> GRANT ALL ON enlightened_tutor.* TO 'enlightened_tutor'@'localhost';
9. Run the SQL in enlightened-tutor.sql
10. Copy config.ini.example to config.ini and fill in the database information
11. $ python3 mtgtop8.py
