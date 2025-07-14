from datetime import datetime


def format_date(d: datetime = datetime.now()) -> str:
    return d.strftime('%Y-%m-%d')


def format_date_compact(d: datetime = datetime.now()) -> str:
    return d.strftime('%Y%m%d')
