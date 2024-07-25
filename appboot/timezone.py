import datetime
import functools
import zoneinfo

from appboot.conf import settings


@functools.lru_cache
def get_default_timezone():
    """
    Return the default time zone as a tzinfo instance.

    This is the time zone defined by settings.TIME_ZONE.
    """
    return zoneinfo.ZoneInfo(settings.TIME_ZONE)


# This function exists for consistency with get_current_timezone_name
def get_default_timezone_name():
    """Return the name of the default time zone."""
    return _get_timezone_name(get_default_timezone())


def _get_timezone_name(timezone):
    """
    Return the offset for fixed offset timezones, or the name of timezone if
    not set.
    """
    return timezone.tzname(None) or str(timezone)


def now():
    """
    Return an aware or naive datetime.datetime, depending on settings.USE_TZ.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc if settings.USE_TZ else None)


def as_default_timezone(dt: datetime.datetime):
    return dt.astimezone(get_default_timezone())
