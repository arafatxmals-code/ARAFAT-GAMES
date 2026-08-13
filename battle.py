from dataclasses import dataclass
@dataclass
class Battle:
    chat_id:int; p1:int; n1:str; p2:int; n2:str
    hp1:int=200; hp2:int=200; turn:int=0; active:bool=True
    def other(self,uid): return self.p2 if uid==self.p1 else self.p1
    def hp(self,uid): return self.hp1 if uid==self.p1 else self.hp2
    def hit(self,uid,d):
        if uid==self.p1:self.hp2=max(0,self.hp2-d)
        else:self.hp1=max(0,self.hp1-d)
