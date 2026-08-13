import asyncio
import random

from config import TURN_SECONDS, STARTING_HP, MIN_DAMAGE, MAX_DAMAGE
from database import result
from .battle import Battle


class GameManager:
    def __init__(self):
        self.waiting = {}
        self.games = {}
        self.tasks = {}

    async def join(self, chat_id, user_id, name, context):
        if user_id in self.games and self.games[user_id].active:
            return "⚔️ You are already in a battle."

        if chat_id in self.waiting:
            old_user_id, old_name = self.waiting.pop(chat_id)

            if old_user_id == user_id:
                self.waiting[chat_id] = (old_user_id, old_name)
                return "⏳ You are already waiting for an opponent."

            battle = Battle(
                chat_id=chat_id,
                p1=old_user_id,
                n1=old_name,
                p2=user_id,
                n2=name,
                hp1=STARTING_HP,
                hp2=STARTING_HP,
                turn=old_user_id,
                active=True,
            )

            self.games[old_user_id] = battle
            self.games[user_id] = battle

            self.start_timer(battle, context)

            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    "🔥 STRONGFIRE BATTLE STARTED!\n\n"
                    f"👤 {old_name} ❤️ {STARTING_HP} HP\n"
                    "⚔️ VS\n"
                    f"👤 {name} ❤️ {STARTING_HP} HP\n\n"
                    f"🎯 Turn: {old_name}\n"
                    f"⏱️ Time: {TURN_SECONDS} seconds\n\n"
                    "🔥 Use /fire"
                ),
            )

            return "⚔️ Opponent found! Battle started."

        self.waiting[chat_id] = (user_id, name)

        return (
            "⏳ Waiting for an opponent...\n\n"
            "Another player can use /play to join."
        )

    async def fire(self, user_id, name, context):
        battle = self.games.get(user_id)

        if not battle or not battle.active:
            return "❌ You don't have an active battle."

        if battle.turn != user_id:
            return "⏳ It's your opponent's turn."

        damage = random.randint(MIN_DAMAGE, MAX_DAMAGE)
        target = battle.other(user_id)

        battle.hit(user_id, damage)
        self.cancel(battle)

        if battle.hp(target) <= 0:
            battle.active = False

            result(user_id, target)

            winner_name = (
                battle.n1 if user_id == battle.p1 else battle.n2
            )
            loser_name = (
                battle.n1 if target == battle.p1 else battle.n2
            )

            await context.bot.send_message(
                chat_id=battle.chat_id,
                text=(
                    "💥 ATTACK!\n\n"
                    f"👤 {name}\n"
                    f"💔 Damage: {damage}\n\n"
                    f"🏆 {winner_name} WINS!\n"
                    f"💀 {loser_name} LOSES!\n\n"
                    "🔥 Battle finished."
                ),
            )

            return "🏆 You won the battle!"

        battle.turn = target
        self.start_timer(battle, context)

        turn_name = (
            battle.n1 if target == battle.p1 else battle.n2
        )

        await context.bot.send_message(
            chat_id=battle.chat_id,
            text=(
                "💥 ATTACK!\n\n"
                f"👤 {name}\n"
                f"💔 Damage: {damage}\n\n"
                f"❤️ {battle.n1}: {battle.hp1} HP\n"
                f"❤️ {battle.n2}: {battle.hp2} HP\n\n"
                f"🎯 Now it's {turn_name}'s turn!\n"
                f"⏱️ {TURN_SECONDS} seconds remaining.\n"
                "🔥 Use /fire"
            ),
        )

        return "🔥 Attack successful."

    def start_timer(self, battle, context):
        self.cancel(battle)
        self.tasks[id(battle)] = asyncio.create_task(
            self.timeout(battle, context)
        )

    def cancel(self, battle):
        task = self.tasks.pop(id(battle), None)

        if task and not task.done():
            task.cancel()

    async def timeout(self, battle, context):
        try:
            await asyncio.sleep(TURN_SECONDS)

            if not battle.active:
                return

            loser = battle.turn
            winner = battle.other(loser)

            battle.active = False
            self.cancel(battle)

            result(winner, loser)

            winner_name = (
                battle.n1 if winner == battle.p1 else battle.n2
            )
            loser_name = (
                battle.n1 if loser == battle.p1 else battle.n2
            )

            await context.bot.send_message(
                chat_id=battle.chat_id,
                text=(
                    "⏰ TIME'S UP!\n\n"
                    f"❌ {loser_name} did not use /fire "
                    f"within {TURN_SECONDS} seconds.\n\n"
                    f"🏆 {winner_name} WINS AUTOMATICALLY!\n"
                    "🔥 Battle finished."
                ),
            )

        except asyncio.CancelledError:
            pass
