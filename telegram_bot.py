# telegram_bot_web.py
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from aiohttp import web
from extract_article import extract_and_summarize

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", "8000"))

# --- простой хэндлер /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает!")

# --- хэндлер /summarize для статей ---
async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Отправь команду вместе с ссылкой на статью: /summarize <URL>")
        return
    url = context.args[0]
    msg = await update.message.reply_text("Собираю статью и делаю краткий пересказ...")
    try:
        result = extract_and_summarize(url)
        summary_text = result.get("summary_text", "Нет результата")
        title = result.get("title", "No title")
        published = result.get("published", "Unknown date")
        response = f"*{title}* ({published})\n\n{summary_text}"
        await msg.edit_text(response, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"Ошибка при обработке статьи:\n{e}")

# --- веб-сервер для Render ---
async def handle(request):
    return web.Response(text="OK")

async def main():
    # 1️⃣ Запуск веб-сервера
    app_web = web.Application()
    app_web.router.add_get("/", handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server listening on port {PORT}")

    # 2️⃣ Настройка бота
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("summarize", summarize))

    # 3️⃣ Запуск polling в фоне
    bot_task = asyncio.create_task(app_bot.run_polling())

    # 4️⃣ Ждём polling и веб вместе
    await bot_task

if __name__ == "__main__":
    asyncio.run(main())
