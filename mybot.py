import asyncio
import os
import random
from datetime import datetime
from typing import Optional, Tuple, List
import logging

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandObject
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POLITICAL_KEYWORDS = {
    'политик', 'президент', 'правительство', 'парламент', 'выборы', 'голосование',
    'партия', 'революция', 'государственный', 'власть', 'министр', 'депутат',
    'закон', 'конституция', 'санкции', 'протест', 'митинг', 'оппозиция',
    'переворот', 'импичмент', 'инаугурация', 'саммит', 'демонстрация', 'референдум'
}

load_dotenv("secret.env")
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

MONTH = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
    7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

API = "https://ru.wikipedia.org/api/rest_v1/feed/onthisday"
REQUEST_TIMEOUT = 10
MAX_ATTEMPTS = 30
CURRENT_YEAR = datetime.now().year

HELP_TEXT = """
<b>Команды Historius:</b>
/today — события текущего дня
/holidays — праздники сегодня
/random — случайная дата и событи
/year &lt;год&gt; — 5 событий выбранного года
"""


def is_political(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in POLITICAL_KEYWORDS)


async def fetch_json(url: str):
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            async with s.get(url) as r:
                if r.status == 200:
                    return await r.json()
                logger.error(f"API request failed: {r.status} {await r.text()}")
                return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


async def get_event(m: int, d: int) -> Optional[Tuple[str, str]]:
    data = await fetch_json(f"{API}/events/{m}/{d}")
    if not data:
        return None

    events = data.get("events", [])
    if not events:
        return None


    non_political_events = [ev for ev in events if not is_political(ev.get("text", ""))]

    if not non_political_events:
        return None

    ev = random.choice(non_political_events)
    return ev.get("year", "???"), ev.get("text", "Нет описания.")


async def get_holidays(m: int, d: int) -> List[str]:
    data = await fetch_json(f"{API}/holidays/{m}/{d}")
    if not data:
        return []
    return [h["text"] for h in data.get("holidays", [])]


async def get_year_events(year: int, limit: int = 5) -> List[str]:
    events: List[str] = []
    tried_dates = set()
    attempts = 0

    while len(events) < limit and attempts < MAX_ATTEMPTS:
        attempts += 1
        m = random.randint(1, 12)
        d = random.randint(1, 31)

        if m == 2 and d > 28:
            d = 28

        if (m, d) in tried_dates:
            continue

        tried_dates.add((m, d))

        try:
            data = await fetch_json(f"{API}/events/{m}/{d}")
            if not data:
                continue

            for ev in data.get("events", []):
                if str(ev.get("year", "")) == str(year):
                    text = ev.get("text", "").strip()
                    if text and not is_political(text):
                        events.append(text)
                        if len(events) >= limit:
                            return events
        except Exception as e:
            logger.error(f"Error processing date {m}/{d}: {e}")
            continue

    return events


def fmt_date(d: int, m: int, y: str | int):
    return f"{d} {MONTH[m]} {y}"


async def today_msg():
    now = datetime.now()
    ev = await get_event(now.month, now.day)
    if not ev:
        return "🤷‍ Сегодня событий не нашёл."
    y, text = ev
    return f"{fmt_date(now.day, now.month, y)}\n\n{text}"


async def random_msg():
    m = random.randint(1, 12)
    d = random.randint(1, 31)
    if m == 2 and d > 28:
        d = 28

    ev = await get_event(m, d)
    if not ev:
        return "🤷‍ В этот день ничего не найдено."
    y, text = ev
    return f"{fmt_date(d, m, y)}\n\n{text}"


async def holidays_msg():
    now = datetime.now()
    hol = await get_holidays(now.month, now.day)
    if not hol:
        return "🎉 Праздники сегодня не найдены."
    random.shuffle(hol)
    sel = hol[:3]
    title = f"🎉 Праздники — {now.day} {MONTH[now.month]}"
    return title + "\n\n" + "\n".join(f"— {h}" for h in sel)


@dp.message(Command("start"))
async def cmd_start(m: Message):
    await m.answer(
        "Привет! Я Historius — бот, который знает все даты. "
        "Используй /help, чтобы увидеть доступные команды."
    )


@dp.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer(HELP_TEXT)


@dp.message(Command("year"))
async def cmd_year(m: Message, command: CommandObject):
    if not command.args or not command.args.isdigit():
        await m.answer("Используй /year &lt;год&gt;, например /year 1812")
        return

    year = int(command.args)

    if year < 1 or year > CURRENT_YEAR:
        await m.answer(f"Пожалуйста, укажите год от 1 до {CURRENT_YEAR}.")
        return

    if year == 2022:
        await m.answer("2022 год временно недоступен для поиска.")
        return

    if year > 2021:
        await m.answer("Пока доступны только года до 2021 включительно.")
        return

    msg = await m.answer(f"🔍 Ищу события {year} года...")

    try:
        evs = await get_year_events(year)
        if not evs:
            await msg.edit_text(f"🤷‍ За {year} год не найдено событий.")
            return

        result = f"📜 События {year} года\n\n" + "\n".join(f"• {e}" for e in evs)
        await msg.edit_text(result)
    except Exception as e:
        logger.error(f"Error in /year command: {e}")
        await msg.edit_text("⚠️ Произошла ошибка при поиске событий. Попробуйте позже.")


@dp.message(Command("today"))
async def cmd_today(m: Message):
    try:
        await m.answer(await today_msg())
    except Exception as e:
        logger.error(f"Error in /today command: {e}")
        await m.answer("⚠️ Не удалось получить события на сегодня.")


@dp.message(Command("holidays"))
async def cmd_holidays(m: Message):
    try:
        await m.answer(await holidays_msg())
    except Exception as e:
        logger.error(f"Error in /holidays command: {e}")
        await m.answer("⚠️ Не удалось получить праздники на сегодня.")


@dp.message(Command("random"))
async def cmd_random(m: Message):
    try:
        await m.answer(await random_msg())
    except Exception as e:
        logger.error(f"Error in /random command: {e}")
        await m.answer("⚠️ Не удалось получить случайное событие.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())