from typing import Any

import mariadb

import config

class Database:
    def __init__(self) -> None:
        self.connection = mariadb.connect(host=config.get('database', 'host'), user=config.get('database', 'user'), password=config.get('database', 'password'), database=config.get('database', 'database'))
        self.cursor = self.connection.cursor(dictionary=True)

    def execute(self, sql: str, args: list, fetch_rows: bool = False) -> list[dict] | int:
        print(sql, args)
        self.cursor.execute(sql, args)
        self.connection.commit()
        if fetch_rows:
            return self.cursor.fetchall()
        return self.cursor.rowcount

def execute(sql: str, args: list) -> int:
    return DB.execute(sql, args)

def select(sql: str, args: list) -> list[dict[str, Any]]:
    return DB.execute(sql, args, fetch_rows=True)

def values(sql: str, args: list) -> list[Any]:
    rs = select(sql, args)
    return [list(row.values())[0] for row in rs]

def insert(sql: str, args: list) -> int:
    return execute(sql, args)

DB = Database()
