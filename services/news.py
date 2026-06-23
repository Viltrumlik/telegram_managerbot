"""Daily top news (image + caption) from RSS feeds."""
import asyncio
import html
import re

import feedparser
import httpx
from bs4 import BeautifulSoup

import config

UA = "Mozilla/5.0 (compatible; ManagerBot/1.0; +https://t.me)"


def _parse_feed(url):
    return feedparser.parse(url, request_headers={"User-Agent": UA})


async def fetch_feed(url):
    return await asyncio.to_thread(_parse_feed, url)


def _extract_image(entry):
    for mc in entry.get("media_content", []) or []:
        if mc.get("url"):
            return mc["url"]
    for mt in entry.get("media_thumbnail", []) or []:
        if mt.get("url"):
            return mt["url"]
    for en in entry.get("enclosures", []) or []:
        if en.get("href") and str(en.get("type", "")).startswith("image"):
            return en["href"]
    for field in ("summary", "content"):
        val = entry.get(field)
        if isinstance(val, list) and val:
            val = val[0].get("value", "")
        if isinstance(val, str):
            m = re.search(r'<img[^>]+src="([^"]+)"', val)
            if m:
                return m.group(1)
    return None


def _upscale_bbc(url):
    if url and "ichef.bbci.co.uk" in url:
        return re.sub(r"/\d+/", "/1200/", url, count=1)
    return url


async def _og_image(link):
    try:
        async with httpx.AsyncClient(
            timeout=15, headers={"User-Agent": UA}, follow_redirects=True
        ) as c:
            r = await c.get(link)
            r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for prop in ("og:image", "twitter:image"):
            tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if tag and tag.get("content"):
                return tag["content"]
    except Exception:
        return None
    return None


def _clean(text):
    if isinstance(text, list) and text:
        text = text[0].get("value", "")
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


async def get_top_story(feed):
    parsed = await fetch_feed(feed["url"])
    if not parsed.entries:
        return None
    e = parsed.entries[0]
    image = _upscale_bbc(_extract_image(e))
    link = e.get("link")
    if not image and link:
        image = await _og_image(link)
    return {
        "lang": feed["lang"],
        "source": feed["name"],
        "title": _clean(e.get("title")),
        "summary": _clean(e.get("summary")),
        "link": link,
        "guid": e.get("id") or link,
        "image": image,
    }


def format_caption(story):
    flag = "🇺🇿" if story["lang"] == "uz" else "🌍"
    cap = f"{flag} <b>{html.escape(story['title'])}</b>\n\n"
    summary = story.get("summary") or ""
    if summary:
        room = 1024 - len(cap) - 140
        if len(summary) > room > 0:
            summary = summary[:room].rsplit(" ", 1)[0] + "…"
        cap += html.escape(summary) + "\n\n"
    cap += f"📰 {html.escape(story['source'])}"
    if story.get("link"):
        cap += f' — <a href="{html.escape(story["link"])}">to\'liq o\'qish</a>'
    return cap


if __name__ == "__main__":
    async def _demo():
        for feed in config.NEWS_FEEDS:
            s = await get_top_story(feed)
            if s:
                print(f"[{s['lang']}] image={bool(s['image'])}")
                print(format_caption(s))
                print("-" * 40)

    asyncio.run(_demo())
