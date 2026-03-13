import os
from dotenv import load_dotenv
from datetime import timezone, timedelta

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in os.getenv("ADMIN_IDS", "").split(",") if admin_id.strip()]

# Фиксированный часовой пояс Еревана (UTC+4)
YEREVAN_TZ = timezone(timedelta(hours=4))
