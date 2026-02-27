import os
import logging
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("Не задан BOT_TOKEN в переменных окружения")

# === Telegram handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен через WebService!")

# Создаём Telegram приложение
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))

# === Web handler ===
async def handle_request(request):
    return web.Response(text="Bot is running")

# === Startup hook ===
async def on_startup(app: web.Application):
    # Запускаем Telegram polling внутри текущего loop
    asyncio.create_task(app_telegram.initialize())   # init application
    asyncio.create_task(app_telegram.start())        # start polling

# === Shutdown hook ===
async def on_cleanup(app: web.Application):
    await app_telegram.stop()
    await app_telegram.shutdown()

# === Aiohttp web app ===
app = web.Application()
app.router.add_get("/", handle_request)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

PORT = int(os.getenv("PORT", 8000))
web.run_app(app, port=PORT)
