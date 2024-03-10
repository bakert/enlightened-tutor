import datetime

import mariadb

import config

Value = int | str | float | bool | datetime.datetime | None
Row = dict[str, Value]
ResultSet = list[Row]


class Database:
    connection: mariadb.Connection
    cursor: mariadb.Cursor

    def __init__(self) -> None:
        self.connect()

    def connect(self) -> None:
        self.connection = mariadb.connect(host=config.get("database", "host"), user=config.get("database", "user"), password=config.get("database", "password"), database=config.get("database", "database"))
        self.cursor = self.connection.cursor(dictionary=True)

    def execute(self, sql: str, args: list[Value], fetch_rows: bool = False) -> ResultSet | int:
        print(sql, args)
        try:
            self.cursor.execute(sql, args)
        except mariadb.InterfaceError as e:
            if "Server has gone away" in str(e):
                print("mariadb Server has gone away, trying to reconnect")
                self.connect()
                return self.cursor.execute(sql, args)  # type: ignore[no-any-return]
            raise
        self.connection.commit()
        if fetch_rows:
            return self.cursor.fetchall()  # type: ignore[no-any-return]
        return self.cursor.rowcount  # type: ignore[no-any-return]


def execute(sql: str, args: list[Value]) -> int:
    return DB.execute(sql, args)  # type: ignore[return-value]


def select(sql: str, args: list[Value]) -> ResultSet:
    return DB.execute(sql, args, fetch_rows=True)  # type: ignore[return-value]


def values(sql: str, args: list[Value]) -> list[Value]:
    rs = select(sql, args)
    return [list(row.values())[0] for row in rs]


def value(sql: str, args: list[Value]) -> Value:
    rs = select(sql, args)
    if rs:
        return list(rs[0].values())[0]
    return None


def insert(sql: str, args: list[Value]) -> int:
    return execute(sql, args)


DB = Database()
