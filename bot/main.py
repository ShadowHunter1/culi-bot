import logging
import time
import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from .handlers import AlertHandler
from .admin import AdminCommands
from .playbook_loader import PlaybookLoader
from .groq_client import GroqClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def main():
    token         = os.environ["TELEGRAM_BOT_TOKEN"]
    groq_api_key  = os.environ["GROQ_API_KEY"]
    groq_model    = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    playbooks_dir = os.environ.get("PLAYBOOKS_DIR", "playbooks")
    bot_username  = os.environ["BOT_USERNAME"]

    playbooks  = PlaybookLoader(playbooks_dir)
    playbooks.load_all()
    groq       = GroqClient(groq_api_key, groq_model)
    start_time = time.time()

    handler = AlertHandler(
        playbook_loader=playbooks,
        groq_client=groq,
        bot_username=bot_username,
    )
    admin = AdminCommands(playbooks, start_time)

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("status",           admin.status))
    app.add_handler(CommandHandler("reload_playbooks", admin.reload_playbooks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))

    logging.info("culi-bot started.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()