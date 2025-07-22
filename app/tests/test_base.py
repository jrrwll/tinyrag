import os
import os.path

from app.config import settings


def _find_first_file() -> str | None:
    local_dir = settings.UPLOAD_DIRECTORY
    print(f"\nwalk local_dir {local_dir}")
    for root, _, files in os.walk(local_dir):
        for file in files:
            return str(os.path.join(root, file))
