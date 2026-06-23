"""Formatting helpers shared across modules."""
import html

# WMO weather code -> (emoji, Uzbek description)
WMO = {
    0: ("☀️", "Ochiq, quyoshli"),
    1: ("🌤", "Asosan ochiq"),
    2: ("⛅️", "Qisman bulutli"),
    3: ("☁️", "Bulutli"),
    45: ("🌫", "Tuman"),
    48: ("🌫", "Qirovli tuman"),
    51: ("🌦", "Yengil shivalama"),
    53: ("🌦", "Shivalama"),
    55: ("🌧", "Kuchli shivalama"),
    56: ("🌧", "Muzli shivalama"),
    57: ("🌧", "Kuchli muzli shivalama"),
    61: ("🌧", "Yengil yomg'ir"),
    63: ("🌧", "Yomg'ir"),
    65: ("🌧", "Kuchli yomg'ir"),
    66: ("🌧", "Muzli yomg'ir"),
    67: ("🌧", "Kuchli muzli yomg'ir"),
    71: ("🌨", "Yengil qor"),
    73: ("🌨", "Qor"),
    75: ("❄️", "Kuchli qor"),
    77: ("🌨", "Qor donachalari"),
    80: ("🌦", "Yomg'irli jala"),
    81: ("🌧", "Jala"),
    82: ("⛈", "Kuchli jala"),
    85: ("🌨", "Qorli jala"),
    86: ("❄️", "Kuchli qorli jala"),
    95: ("⛈", "Momaqaldiroq"),
    96: ("⛈", "Do'l bilan momaqaldiroq"),
    99: ("⛈", "Kuchli do'l bilan momaqaldiroq"),
}


def weather_desc(code):
    return WMO.get(code, ("🌡", "Noma'lum"))


def esc(s):
    return html.escape(str(s))


def fmt_num(n, decimals=0):
    """Group thousands with spaces (Uzbek convention)."""
    if n is None:
        return "—"
    s = f"{n:,.{decimals}f}" if decimals else f"{n:,.0f}"
    return s.replace(",", " ")


def fmt_price(n):
    """Adaptive precision for crypto (handles tiny meme-coin prices)."""
    if n is None:
        return "—"
    if n >= 1000:
        return fmt_num(n, 0)
    if n >= 1:
        return fmt_num(n, 2)
    return f"{n:.8f}".rstrip("0").rstrip(".")


def pct(change):
    """Format a 24h percent change with colored arrow."""
    if change is None:
        return ""
    if change >= 0:
        return f" (🟢 +{change:.1f}%)"
    return f" (🔴 {change:.1f}%)"
