import sqlite3


class AlphaStreetPipeline:
    def __init__(self):
        self.con = sqlite3.connect("alphastreet.db")
        self.cur = self.con.cursor()

        # Create the table if it doesn't exist
        self.cur.execute(
            """
        CREATE TABLE IF NOT EXISTS articles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            category TEXT,
            title TEXT,
            date TEXT,
            link TEXT UNIQUE
        )"""
        )

    def process_item(self, item, spider):
        # Insert the item into the database
        self.cur.execute(
            """INSERT OR IGNORE INTO articles (symbol, category, title, date, link) VALUES (?,?,?,?,?)""",
            (
                item["symbol"],
                item["category"],
                item["title"],
                item["date"],
                item["link"],
            ),
        )
        return item

    def close_spider(self, spider):
        self.con.commit()
        self.con.close()
