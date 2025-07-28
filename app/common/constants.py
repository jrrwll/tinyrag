from datetime import datetime, timezone

APP_NAME = "tinyrag"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"

MIN_UTC_DATETIME = datetime.fromtimestamp(0, tz=timezone.utc)
