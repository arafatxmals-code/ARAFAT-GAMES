import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN
from database import init_db, ensure_user, get_profile, leaderboard, get_role, set_role, add_stars, add_rank_stars, set_rank
from game.game_manager import GameManager
from management.permissions import is_owner, can_manage_stars, can_manage_players

logging.basicConfig(level=logging.INFO)
gm = GameManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u=update.effective_user; ensure_user(u.id,u.username,u.first_name)
    await update.message.reply_text("🔥 STRONGFIRE GAME BOT\n\n/play - battle\n/fire - fire\n/profile - profile\n/rank - rank\n/leaderboard - leaderboard\n/daily - daily reward\n/spin - spin reward\n/shop - shop\n/help - help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 PLAYER: /play /fire /profile /rank /leaderboard /daily /spin /shop\n"
        "👑 MANAGEMENT: /setrole /addstar /removestar /addrankstar /removerankstar /setrank /ban /unban /broadcast"
    )

async def play(update, context):
    u=update.effective_user; ensure_user(u.id,u.username,u.first_name)
    await update.message.reply_text(await gm.join(update.effective_chat.id,u.id,u.first_name,context))

async def fire(update, context):
    u=update.effective_user
    await update.message.reply_text(await gm.fire(u.id,u.first_name,context))

async def profile(update, context):
    u=update.effective_user; ensure_user(u.id,u.username,u.first_name)
    p=get_profile(u.id)
    await update.message.reply_text(f"👤 {p['name']}\n⭐ Stars: {p['stars']}\n🏅 Rank Stars: {p['rank_stars']}\n🏆 Rank: {p['rank']}\n✅ Wins: {p['wins']}\n❌ Losses: {p['losses']}")

async def rank(update, context):
    u=update.effective_user; p=get_profile(u.id)
    await update.message.reply_text(f"🏅 {p['name']}\nRank: {p['rank']}\nRank Stars: {p['rank_stars']}")

async def lb(update, context):
    rows=leaderboard()
    await update.message.reply_text("🏆 LEADERBOARD\n\n" + ("\n".join(f"{i+1}. {r['name']} — {r['wins']} wins" for i,r in enumerate(rows)) or "No players."))

async def setrole_cmd(update, context):
    u=update.effective_user
    if not is_owner(u.id): return await update.message.reply_text("❌ Owner only.")
    if len(context.args)<2: return await update.message.reply_text("Usage: /setrole USER_ID ROLE")
    set_role(int(context.args[0]),context.args[1].lower()); await update.message.reply_text("✅ Role updated.")

async def star_cmd(update, context):
    u=update.effective_user
    if not can_manage_stars(u.id): return await update.message.reply_text("❌ Permission denied.")
    if len(context.args)<2: return await update.message.reply_text("Usage: /addstar USER_ID AMOUNT")
    add_stars(int(context.args[0]),int(context.args[1])); await update.message.reply_text("⭐ Stars added.")

async def removestar_cmd(update, context):
    u=update.effective_user
    if not can_manage_stars(u.id): return await update.message.reply_text("❌ Permission denied.")
    if len(context.args)<2: return await update.message.reply_text("Usage: /removestar USER_ID AMOUNT")
    add_stars(int(context.args[0]),-int(context.args[1])); await update.message.reply_text("⭐ Stars removed.")

async def addrank_cmd(update, context):
    u=update.effective_user
    if not can_manage_stars(u.id): return await update.message.reply_text("❌ Permission denied.")
    if len(context.args)<2: return await update.message.reply_text("Usage: /addrankstar USER_ID AMOUNT")
    add_rank_stars(int(context.args[0]),int(context.args[1])); await update.message.reply_text("🏅 Rank Stars added.")

async def removerank_cmd(update, context):
    u=update.effective_user
    if not can_manage_stars(u.id): return await update.message.reply_text("❌ Permission denied.")
    if len(context.args)<2: return await update.message.reply_text("Usage: /removerankstar USER_ID AMOUNT")
    add_rank_stars(int(context.args[0]),-int(context.args[1])); await update.message.reply_text("🏅 Rank Stars removed.")

async def setrank_cmd(update, context):
    u=update.effective_user
    if not can_manage_players(u.id): return await update.message.reply_text("❌ Permission denied.")
    if len(context.args)<2: return await update.message.reply_text("Usage: /setrank USER_ID RANK")
    set_rank(int(context.args[0])," ".join(context.args[1:])); await update.message.reply_text("🏅 Rank set.")

async def daily(update, context):
    await update.message.reply_text("🎁 Daily reward system is ready for expansion.")

async def spin(update, context):
    await update.message.reply_text("🎰 Spin system is ready for expansion.")

async def shop(update, context):
    await update.message.reply_text("🛒 Shop system is ready for expansion.")

def main():
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN is missing.")
    init_db()
    app=Application.builder().token(BOT_TOKEN).build()
    handlers=[
        ("start",start),("help",help_cmd),("play",play),("fire",fire),
        ("profile",profile),("rank",rank),("leaderboard",lb),("daily",daily),
        ("spin",spin),("shop",shop),("setrole",setrole_cmd),("addstar",star_cmd),
        ("removestar",removestar_cmd),("addrankstar",addrank_cmd),
        ("removerankstar",removerank_cmd),("setrank",setrank_cmd)
    ]
    for n,f in handlers: app.add_handler(CommandHandler(n,f))
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__": main()
