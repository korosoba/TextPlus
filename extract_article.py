# extract_article.py

import trafilatura
from datetime import datetime
from pathlib import Path
import os

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def extract_and_summarize(url: str) -> dict:
    """
    Извлекает статью и делает Groq-саммари.
    Возвращает словарь с результатами.
    """

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise Exception("Не удалось скачать страницу")

    metadata = trafilatura.extract_metadata(downloaded)

    title = getattr(metadata, "title", "No title") if metadata else "No title"
    pub_date = getattr(metadata, "date", None)
    if not pub_date:
        pub_date = datetime.utcnow().strftime("%Y-%m-%d")

    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        include_links=False,
        include_formatting=False,
        favor_precision=True,
    )

    if not text or len(text.strip()) < 300:
        raise Exception("Не удалось извлечь текст статьи")

    if not GROQ_AVAILABLE:
        raise Exception("Библиотека groq не установлена")

    if not os.getenv("GROQ_API_KEY"):
        raise Exception("Не задан GROQ_API_KEY")

    client = Groq()

    preview_text = text[:12000].strip()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты эксперт по кино и сериалам. "
                    "Напиши краткий пересказ статьи на русском языке (180–350 слов). "
                    "Сфокусируйся на ключевых идеях, анализе и контексте. "
                    "Избегай спойлеров."
                )
            },
            {
                "role": "user",
                "content": f"Статья:\n{preview_text}"
            }
        ],
        temperature=0.5,
        max_tokens=600,
        top_p=0.9
    )

    summary_text = response.choices[0].message.content.strip()

    return {
        "title": title,
        "published": pub_date,
        "text_length": len(text),
        "summary_text": summary_text,
        "model": response.model
    }