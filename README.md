# ManagerBot 🤖

Shaxsiy Telegram "menejer" bot. Avtomatik ravishda quyidagilarni qiladi:

| Funksiya | Vaqt | Manba (bepul API) |
|---|---|---|
| ☀️ Ob-havo (Farg'ona) | har kuni 07:00 | Open-Meteo |
| 💱 Valyuta kurslari (UZS) | har kuni 07:00 | CBU (cbu.uz) |
| 📰 Yangiliklar (rasm + matn) | har kuni 08:00 | Daryo + BBC RSS |
| 🕌 Namoz eslatmalari | har namozdan 10 daq oldin | Aladhan |
| 💰 Kripto + aksiyalar | har 6 soatda | CoinGecko + Yahoo/Finnhub |
| 💱 Inline konvertatsiya | istalgan chatda `@bot 100 usd uzs` | exchangerate-api.com |

## Buyruqlar
`/start` `/help` `/obhavo` `/kurs` `/yangilik` `/namoz` `/kripto`

## Local ishga tushirish
```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env        # BOT_TOKEN ni kiriting
venv/bin/python bot.py
```

## Har bir servisni alohida tekshirish
```bash
venv/bin/python -m services.weather
venv/bin/python -m services.currency
venv/bin/python -m services.news
venv/bin/python -m services.prayer
venv/bin/python -m services.crypto
venv/bin/python -m services.stocks
```

## Sozlash
Tahrirlash uchun `config.py`: shahar/koordinatalar, coin/aksiya ro'yxati,
yuborish vaqtlari, valyutalar, namoz hisoblash usuli.

## Deploy
`deploy/DEPLOY.md` ga qarang (VPS + systemd, 24/7).

## Maxfiylik
Sirlar faqat `.env` faylida (git'ga kiritilmaydi). Inline rejim BotFather'da
`/setinline` orqali yoqilishi kerak.
