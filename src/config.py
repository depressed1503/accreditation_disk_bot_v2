from pathlib import Path
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR.parent / ".env"

load_dotenv(ENV_PATH)

SETTINGS = {
    "YADISK_TOKEN": os.environ.get("YADISK_TOKEN"),
    "TELEGRAM_TOKEN": os.environ.get("TELEGRAM_TOKEN"),
    "ADMIN_IDS": [int(id) for id in os.environ.get("ADMIN_IDS", "").split(",") if id.isnumeric()]
}

if __name__ == "__main__":
    print(SETTINGS)
