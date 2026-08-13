import asyncio
import random

from config import (
    TURN_SECONDS,
    STARTING_HP,
    MIN_DAMAGE,
    MAX_DAMAGE,
)
from database import result
from .battle import Battle


class GameManager:
    def __init__(self):
        self.waiting = {}
        self.games = {}
        self.tasks = {}

    async def join(self, chat_id, user_id, name, context):
        # Already playing
        if user_id in self.games:
            battle = self.games[user_id]
            if battle.active:
                return "⚔️ You are already in a battle."

        # Already waiting
        if chat_id in self.waiting:
            old_user_id, old_name = self.waiting[chat_id]

            if old_user_id == user_id:
                return "⏳ You are already waiting for an opponent."

            # Create battle
            self.waiting.pop(chat_id, None)

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

        # First player enters waiting queue
        self.waiting[chat_id] = (user_id, name)

        return (
            "⏳ Waiting for an opponent...\n\n"
            "Another player can use /play to start the battle."
        )

    async def fire(self, user_id, name, context):
        battle = self.games.get(user_id)

        # No battle
        if not battle or not battle.active:
            return "❌ You don't have an active battle."

        # Wrong turn
        if battle.turn != user_id:
            return "⏳ It's your opponent's turn."

        # Random damage
        damage = random.randint(MIN_DAMAGE, MAX_DAMAGE)

        target = battle.other(user_id)

        # Apply damage
        battle.hit(user_id, damage)

        # Cancel current timer
        self.cancel(battle)

        # Check winner
        if battle.hp(target) <= 0:
            battle.active = False

            winner_id = user_id
            loser_id = target

            result(winner_id, loser_id)

            winner_name = (
                battle.n1
                if winner_id == battle.p1
                else battle.n2
            )

            loser_name = (
                battle.n1
                if loser_id == battle.p1
                else battle.n2
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

        # Next player's turn
        battle.turn = target

        # Start 30-second timer for next player
        self.start_timer(battle, context)

        turn_name = (
            battle.n1
            if target == battle.p1
            else battle.n2
        )

        await context.bot.send_message(
            chat_id=battle.chat_id,
            text=(
                "💥 ATTACK!\n\n"
                f"👤 {name}\n"
                f"💔 Damage: {damage}\n\n"
                f"❤️ {battle.n1}: {battle.hp1} HP\n"
                f"❤️ {battle.n2}: {battle.hp2}
