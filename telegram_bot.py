import os
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("Не задан BOT_TOKEN в переменных окружения")

# Пример хэндлера /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает через WebService!")

# Создаём приложение Telegram
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))

# Адаптация под Render WebService
async def handle_request(request):
    # Можно проверять /health или просто отвечать OK
    return web.Response(text="Bot is running")

async def start_bot(app):
    """Запускаем polling в фоне"""
    # polling запускается как таск
    import asyncio
    asyncio.create_task(app_telegram.run_polling())

# Создаём aiohttp веб-приложение
app = web.Application()
app.router.add_get("/", handle_request)
app.on_startup.append(lambda app: start_bot(app))

# Render задаёт порт через переменную окружения PORT
PORT = int(os.getenv("PORT", 8000))
web.run_app(app, port=PORT)
