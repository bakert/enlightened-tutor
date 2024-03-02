import mariadb

import config
class Database:
    def __init__(self) -> None:
        self.connection = mariadb.connect(host=config.get('database', 'host'), user=config.get('database', 'user'), password=config.get('database', 'password'), database=config.get('database', 'database'))
        self.cursor = self.connection.cursor()

    def execute(self, sql: str, args: list, fetch_rows: bool = False) -> list[dict] | int:
        print(sql, args)
        self.cursor.execute(sql, args)
        self.connection.commit()
        if fetch_rows:
            return self.cursor.fetchall()
        return self.cursor.rowcount


def select(sql: str, args: list) -> list[dict]:
    return DB.execute(sql, args, fetch_rows=True)

def insert(sql: str, args: list) -> int:
    return DB.execute(sql, args)

DB = Database()
