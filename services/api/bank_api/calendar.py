"""Pinned synthetic service calendar. No claims about statutory/bank calendars."""

from datetime import datetime, time, timedelta
from importlib.resources import files
from zoneinfo import ZoneInfo

VERSION = "demo-calendar-v1"
HOLIDAYS = ("2026-10-12",)  # Explicit synthetic fixture; not a statutory calendar.
with files("tzdata.zoneinfo").joinpath("America", "Winnipeg").open("rb") as f:
    ZONE = ZoneInfo.from_file(f, key="America/Winnipeg")


def service_date(day, holidays=HOLIDAYS):
    return day.weekday() < 5 and day.isoformat() not in holidays


def add_hours(start, hours, holidays=HOLIDAYS):
    current = start.astimezone(ZONE)
    remaining = timedelta(hours=hours)
    while remaining > timedelta(0):
        opening = datetime.combine(current.date(), time(9), ZONE)
        closing = datetime.combine(current.date(), time(17), ZONE)
        if not service_date(current.date(), holidays) or current >= closing:
            current = datetime.combine(current.date() + timedelta(days=1), time(9), ZONE)
            continue
        current = max(current, opening)
        available = closing - current
        used = min(remaining, available)
        current += used
        remaining -= used
    return current


def contact_window(first, holidays=HOLIDAYS):
    day = first.astimezone(ZONE).date()
    count = 0
    while True:
        if service_date(day, holidays):
            count += 1
        if count == 3:
            return datetime.combine(day, time(17), ZONE)
        day += timedelta(days=1)
