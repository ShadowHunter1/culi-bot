import time
from telegram import Update
from telegram.ext import ContextTypes
from .playbook_loader import PlaybookLoader

class AdminCommands:
    def __init__(self, playbooks: PlaybookLoader, start_time: float):
        self.playbooks = playbooks
        self.start_time = start_time

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        playbook_count = len(self.playbooks._cache)
        await update.message.reply_text(
            f"✅ <b>culi-bot đang hoạt động</b>\n"
            f"⏱ Uptime: {hours}h {minutes}m {seconds}s\n"
            f"📚 Playbooks đã load: {playbook_count}",
            parse_mode="HTML",
        )

    async def reload_playbooks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.playbooks.load_all()
        count = len(self.playbooks._cache)
        await update.message.reply_text(
            f"✅ Đã reload {count} playbooks từ filesystem.",
            parse_mode="HTML",
        )