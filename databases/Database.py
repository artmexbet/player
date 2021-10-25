import sqlite3
from typing import List
import os

DATABASE_PATH = "databases/database.db"


class Database:
    def __init__(self):
        self.base = sqlite3.connect(DATABASE_PATH)
        self.cur = self.base.cursor()

    def get_all_tables(self) -> List[tuple]:
        return self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

    def create_playlist(self, name):
        self.cur.execute("""CREATE TABLE ? (
                            id             INTEGER PRIMARY KEY AUTOINCREMENT
                                                   NOT NULL
                                                   UNIQUE,
                            music_name     STRING,
                            path           STRING  NOT NULL,
                            repeated_count INTEGER DEFAULT (0));
                            """, (name,))


class Playlist:
    def __init__(self, name, database):
        super().__init__()
        self.name = name
        self.database = database

    def get_all_tracks(self) -> List[tuple]:
        temp = []
        for line in self.database.cur.execute(f"SELECT * FROM {self.name}").fetchall():
            if os.path.exists(line[2]) and os.path.isfile(line[2]):
                temp.append(line)
            else:
                self.database.cur.execute(f"DELETE * FROM {self.name} WHERE id={line[0]}")
        return temp

    def get_formatted_tracks(self) -> List[str]:
        temp = []
        for line in self.get_all_tracks():
            if line[1]:
                temp.append(f"{line[0]}: {line[1]}\t{line[3]}")
            else:
                temp.append(f"{line[0]}: {line[2][:15]}...\t{line[3]}")
        return temp

    def get_paths(self) -> List[str]:
        return [i[2] for i in self.get_all_tracks()]

    def add_track(self, name: str, path: str):
        self.database.cur.execute(f"INSERT INTO {self.name}(music_name, path) VALUES ('{name}', '{path}')")
        self.database.base.commit()

    def __getitem__(self, item) -> tuple:
        return self.database.cur.execute(f"SELECT * FROM {self.name} WHERE id={item}").fetchone()
