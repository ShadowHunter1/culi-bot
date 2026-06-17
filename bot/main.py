import logging
import time
import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from .handlers import AlertHandler
from .admin import AdminCommands
from .playbook_loader import PlaybookLoader
from .grok_client import GrokClient
from .database import Database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def main():
    token         = os.environ["TELEGRAM_BOT_TOKEN"]
    grok_api_key  = os.environ["GROK_API_KEY"]
    grok_model    = os.environ.get("GROK_MODEL", "grok-3")
    db_path       = os.environ.get("DATABASE_PATH", "data/culi_bot.db")
    playbooks_dir = os.environ.get("PLAYBOOKS_DIR", "playbooks")
    bot_username  = os.environ["BOT_USERNAME"]  # Ví dụ: culi_bot

    # Khởi tạo components
    db       = Database(db_path)
    playbooks = PlaybookLoader(playbooks_dir)
    playbooks.load_all()
    grok     = GrokClient(grok_api_key, grok_model)
    start_time = time.time()

    handler = AlertHandler(
        playbook_loader=playbooks,
        grok_client=grok,
        database=db,
        bot_username=bot_username,
    )
    admin = AdminCommands(db, playbooks, start_time)

    app = ApplicationBuilder().token(token).build()

    # Đăng ký handlers
    app.add_handler(CommandHandler("status",           admin.status))
    app.add_handler(CommandHandler("stats",            admin.stats))
    app.add_handler(CommandHandler("recent",           admin.recent))
    app.add_handler(CommandHandler("reload_playbooks", admin.reload_playbooks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))

    logging.info("culi-bot started.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()