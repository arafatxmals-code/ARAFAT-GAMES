from database import get_role


LEVEL = {
    "user": 0,
    "moderator": 1,
    "admin": 2,
    "ceo": 3,
    "owner": 4,
}


def get_level(user_id):
    role = get_role(user_id)
    return LEVEL.get(role, 0)


def is_owner(user_id):
    return get_level(user_id) >= LEVEL["owner"]


def is_ceo(user_id):
    return get_level(user_id) >= LEVEL["ceo"]


def is_admin(user_id):
    return get_level(user_id) >= LEVEL["admin"]


def is_moderator(user_id):
    return get_level(user_id) >= LEVEL["moderator"]


def can_manage_stars(user_id):
    return get_level(user_id) >= LEVEL["admin"]


def can_manage_players(user_id):
    return get_level(user_id) >= LEVEL["admin"]


def can_manage_groups(user_id):
    return get_level(user_id) >= LEVEL["admin"]
