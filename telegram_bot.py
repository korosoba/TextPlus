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
    async def polling_task():
        # run_polling в таске, не закрывает event loop
        await app_telegram.run_polling(close_loop=False)
    asyncio.create_task(polling_task())

# === Aiohttp web app ===
app = web.Application()
app.router.add_get("/", handle_request)
app.on_startup.append(on_startup)

PORT = int(os.getenv("PORT", 8000))
web.run_app(app, port=PORT)
