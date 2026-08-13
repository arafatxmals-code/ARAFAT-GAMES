from database import get_role
LEVEL={"user":0,"moderator":1,"admin":2,"ceo":3,"owner":4}
def level(uid): return LEVEL.get(get_role(uid),0)
def is_owner(uid): return level(uid)>=4
def can_manage_stars(uid): return level(uid)>=2
def can_manage_players(uid): return level(uid)>=2
