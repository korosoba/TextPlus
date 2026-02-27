# telegram_bot.py

import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from extract_article import extract_and_summarize

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ALLOWED_DOMAINS = [
    "screenrant.com",
    "cbr.com",
    "collider.com",
    "movieweb.com"
]


def is_valid_url(url: str) -> bool:
    return any(domain in url.lower() for domain in ALLOWED_DOMAINS)


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("Это не похоже на ссылку. Отправь URL статьи.")
        return

    if not is_valid_url(url):
        await update.message.reply_text(
            "Ссылка должна быть с screenrant.com, cbr.com, collider.com или movieweb.com."
        )
        return

    await update.message.reply_text("Обрабатываю статью (30–60 секунд)...")

    try:
        result = extract_and_summarize(url)

        temp_filename = "summary.txt"

        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(f"Title: {result['title']}\n")
            f.write(f"Published: {result['published']}\n")
            f.write(f"Model: {result['model']}\n")
            f.write("-" * 60 + "\n\n")
            f.write(result["summary_text"])

        await update.message.reply_document(
            document=open(temp_filename, "rb"),
            caption=f"Готово:\n{result['title']}"
        )

        os.remove(temp_filename)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise Exception("Не задан TELEGRAM_BOT_TOKEN")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    print("Бот запущен и ожидает сообщений...")

    app.run_polling()


if __name__ == "__main__":
    main()