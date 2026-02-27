import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from extract_article import process_article

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь ссылку на статью.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("Пожалуйста, отправь корректную ссылку.")
        return

    await update.message.reply_text("Обрабатываю статью...")

    try:
        result = process_article(url)
        await update.message.reply_text(result[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен и ожидает сообщений...")

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
