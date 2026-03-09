import sqlite3

DB = "insider_risk.db"

def init_db():

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        action TEXT,
        file TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        severity TEXT,
        message TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_scores(
        user TEXT PRIMARY KEY,
        score INTEGER
    )
    """)

    conn.commit()
    conn.close()


def insert_log(user,action,file,timestamp):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO logs(user,action,file,timestamp) VALUES(?,?,?,?)",
        (user,action,file,timestamp)
    )

    conn.commit()
    conn.close()    


if __name__ == "__main__":
    init_db()