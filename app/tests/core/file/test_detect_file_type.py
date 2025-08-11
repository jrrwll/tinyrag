from app.config import settings
from app.core.file.file_type import detect_file_type
import os

def test_detect_file_type():
    local_dir = settings.UPLOAD_DIRECTORY
    print(f"\nwalk local_dir {local_dir}")
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)

            print(f"{local_path}: {detect_file_type(local_path)}")
