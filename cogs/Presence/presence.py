import pypresence
import time
import sqlite3 as sql
rp = pypresence.Presence(client_id=867111922549784597)
rp.connect()
rp.update(state="Watching your children", details="Chill it's a joke", large_image="large", large_text="Teehee it tickles", buttons=[{"label": "Steam Profile", "url": "https://steamcommunity.com/profiles/76561199089500781/"}])
print("started")
while True:
    db = sql.connect()
    sql.execute("SELECT FROM")
    time.sleep(15)