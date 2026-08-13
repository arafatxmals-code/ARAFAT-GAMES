import asyncio,random
from config import TURN_SECONDS,STARTING_HP,MIN_DAMAGE,MAX_DAMAGE
from database import result
from .battle import Battle
class GameManager:
    def __init__(self): self.wait={}; self.games={}; self.tasks={}
    async def join(self,chat,uid,name,context):
        if uid in self.games and self.games[uid].active:return "⚔️ Already in battle."
        key=chat
        if key not in self.wait:
            self.wait[key]=(uid,name); return "⏳ Waiting for an opponent..."
        a,an=self.wait.pop(key)
        if a==uid:return "❌ You cannot battle yourself."
        b=Battle(chat,a,an,uid,name,STARTING_HP,STARTING_HP,a)
        self.games[a]=self.games[uid]=b; self.start_timer(b,context)
        await context.bot.send_message(chat_id=chat,text=f"🔥 BATTLE START!\n{an} VS {name}\n❤️ HP: 200 / 200\n🎯 {an}'s turn\n⏱️ 30 seconds\nUse /fire")
        return "⚔️ Battle found! Check the group."
    async def fire(self,uid,name,context):
        b=self.games.get(uid)
        if not b or not b.active:return "❌ No active battle."
        if b.turn!=uid:return "⏳ Not your turn."
        d=random.randint(MIN_DAMAGE,MAX_DAMAGE); b.hit(uid,d)
        target=b.other(uid)
        if b.hp(target)<=0:
            b.active=False; self.cancel(b); result(uid,target)
            await context.bot.send_message(b.chat_id,text=f"💥 {name} dealt {d} damage!\n🏆 {name} WINS!")
            return "🏆 Battle finished."
        b.turn=target; self.start_timer(b,context)
        hp=f"❤️ {b.n1}: {b.hp1}\n❤️ {b.n2}: {b.hp2}"
        await context.bot.send_message(b.chat_id,text=f"💥 {name} fired! Damage: {d}\n{hp}\n🎯 Next turn: {'your opponent' if target!=uid else 'you'}\n⏱️ 30 seconds")
        return "🔥 Attack sent."
    def start_timer(self,b,c):
        self.cancel(b); self.tasks[id(b)]=asyncio.create_task(self.timeout(b,c))
    def cancel(self,b):
        t=self.tasks.pop(id(b),None)
        if t and not t.done():t.cancel()
    async def timeout(self,b,c):
        try:
            await asyncio.sleep(TURN_SECONDS)
            if not b.active:return
            loser=b.turn; winner=b.other(loser); b.active=False; result(winner,loser)
            wn=b.n1 if winner==b.p1 else b.n2; ln=b.n1 if loser==b.p1 else b.n2
            await c.bot.send_message(b.chat_id,text=f"⏰ 30 seconds finished!\n🏆 {wn} WINS automatically!\n❌ {ln} did not use /fire.")
        except asyncio.CancelledError: pass
