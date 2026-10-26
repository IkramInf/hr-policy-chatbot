
from datetime import date, datetime
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = "Asia/Dhaka"


def get_today(timezone_name: str = DEFAULT_TIMEZONE) -> date:
    """Return today's date in the configured timezone."""
    return datetime.now(ZoneInfo(timezone_name)).date()


def get_formatted_date(
    timezone_name: str = DEFAULT_TIMEZONE,
) -> str:
    """Return a human-readable date, e.g. October 26, 2026."""
    return get_today(timezone_name).strftime("%B %d, %Y").replace(
        " 0", " "
    )
