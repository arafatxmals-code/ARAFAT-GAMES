from dataclasses import dataclass


@dataclass
class Battle:
    chat_id: int
    p1: int
    n1: str
    p2: int
    n2: str
    hp1: int = 200
    hp2: int = 200
    turn: int = 0
    active: bool = True

    def other(self, user_id):
        if user_id == self.p1:
            return self.p2
        return self.p1

    def hp(self, user_id):
        if user_id == self.p1:
            return self.hp1
        return self.hp2

    def hit(self, user_id, damage):
        if user_id == self.p1:
            self.hp2 = max(0, self.hp2 - damage)
        else:
            self.hp1 = max(0, self.hp1 - damage)
