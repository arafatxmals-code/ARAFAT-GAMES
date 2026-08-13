import sqlite3
from config import DATABASE_PATH, OWNER_ID
RANKS=["Bronze","Silver","Gold","Platinum","Diamond","Master"]

def db():
    c=sqlite3.connect(DATABASE_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY, username TEXT, name TEXT, role TEXT DEFAULT 'user',
        stars INTEGER DEFAULT 0, rank_stars INTEGER DEFAULT 0, rank TEXT DEFAULT 'Bronze',
        wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, games INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0)""")
        c.commit()
    if OWNER_ID: ensure_user(OWNER_ID,"owner","Owner"); set_role(OWNER_ID,"owner")

def ensure_user(uid,username,name):
    with db() as c:
        c.execute("INSERT OR IGNORE INTO users(user_id,username,name) VALUES(?,?,?)",(uid,username or "",name or "Player"))
        c.execute("UPDATE users SET username=?,name=? WHERE user_id=?",(username or "",name or "Player",uid)); c.commit()
def get_profile(uid):
    with db() as c: return dict(c.execute("SELECT * FROM users WHERE user_id=?",(uid,)).fetchone())
def leaderboard():
    with db() as c: return c.execute("SELECT name,wins FROM users WHERE banned=0 ORDER BY wins DESC LIMIT 10").fetchall()
def get_role(uid):
    if uid==OWNER_ID: return "owner"
    with db() as c:
        r=c.execute("SELECT role FROM users WHERE user_id=?",(uid,)).fetchone()
        return r["role"] if r else "user"
def set_role(uid,role):
    ensure_user(uid,"","Player")
    with db() as c: c.execute("UPDATE users SET role=? WHERE user_id=?",(role,uid)); c.commit()
def add_stars(uid,n):
    with db() as c: c.execute("UPDATE users SET stars=MAX(0,stars+?) WHERE user_id=?",(n,uid)); c.commit()
def add_rank_stars(uid,n):
    with db() as c: c.execute("UPDATE users SET rank_stars=MAX(0,rank_stars+?) WHERE user_id=?",(n,uid)); c.commit()
def set_rank(uid,r):
    with db() as c: c.execute("UPDATE users SET rank=? WHERE user_id=?",(r,uid)); c.commit()
def result(winner,loser):
    with db() as c:
        c.execute("UPDATE users SET wins=wins+1,games=games+1,stars=stars+20 WHERE user_id=?",(winner,))
        c.execute("UPDATE users SET losses=losses+1,games=games+1 WHERE user_id=?",(loser,)); c.commit()
