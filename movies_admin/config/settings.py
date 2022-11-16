import os

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    "components/common.py",
    "components/database.py",
    "components/production.py",
)

DEBUG = os.getenv("DEBUG", False) == "True"

if DEBUG:
    include("components/development.py")
