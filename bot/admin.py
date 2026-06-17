import time
from telegram import Update
from telegram.ext import ContextTypes
from .database import Database
from .playbook_loader import PlaybookLoader

class AdminCommands:
    def __init__(self, db: Database, playbooks: PlaybookLoader, start_time: float):
        self.db = db
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

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = self.db.get_stats()
        lines = [f"📊 <b>Thống kê 30 ngày qua</b>\nTổng alert: {data['total']}\n\n<b>Top alerts:</b>"]
        for item in data["top_alerts"]:
            lines.append(f"• {item['alertname']}: {item['cnt']} lần")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")

    async def recent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        rows = self.db.get_recent(5)
        if not rows:
            await update.message.reply_text("Chưa có alert nào được xử lý.")
            return
        lines = ["🕐 <b>5 alert gần nhất:</b>"]
        for r in rows:
            ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["created_at"]))
            lines.append(f"• [{ts}] <b>{r['alertname']}</b> | {r['namespace']} | {r['severity']}")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")

    async def reload_playbooks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.playbooks.load_all()
        count = len(self.playbooks._cache)
        await update.message.reply_text(
            f"✅ Đã reload {count} playbooks từ filesystem.",
            parse_mode="HTML",
        )