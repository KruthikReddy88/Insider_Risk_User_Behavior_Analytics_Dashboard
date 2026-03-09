import sqlite3

conn = sqlite3.connect("src/DB/insider_risk.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM risk_data_final")

conn.commit()
conn.close()

print("Database reset complete.")