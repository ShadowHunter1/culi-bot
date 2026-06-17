import logging
from telegram import Update
from telegram.ext import ContextTypes
from .parser import parse_alert_message
from .playbook_loader import PlaybookLoader
from .groq_client import GroqClient
from .database import Database

logger = logging.getLogger(__name__)

class AlertHandler:
    def __init__(
        self,
        playbook_loader: PlaybookLoader,
        grok_client: GroqClient,
        database: Database,
        bot_username: str,
        dedup_enabled: bool = True,
        dedup_cooldown: int = 1800,
    ):
        self.playbooks = playbook_loader
        self.grok = grok_client
        self.db = database
        self.bot_username = bot_username.lstrip("@")
        self.dedup_enabled = dedup_enabled
        self.dedup_cooldown = dedup_cooldown

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if not message or not message.text:
            return

        text = message.text

        # Chỉ xử lý khi được mention
        mention = f"@{self.bot_username}"
        if mention not in text:
            return

        # Parse alert
        alert = parse_alert_message(text)
        if not alert:
            logger.info("Message có mention nhưng không phải alert, bỏ qua.")
            return

        alert_hash = self.db.make_hash(alert.alertname, alert.namespace)

        # Dedup check
        if self.dedup_enabled and self.db.check_dedup(alert_hash, self.dedup_cooldown):
            await message.reply_text(
                f"⚠️ Alert <b>{alert.alertname}</b> đã được phân tích gần đây.\n"
                "Xem lại response trước hoặc chờ hết cooldown (30 phút).",
                parse_mode="HTML",
                reply_to_message_id=message.message_id,
            )
            return

        # Load playbook
        category, playbook_content = self.playbooks.get_for_alert(alert.alertname)

        # Typing indicator
        await context.bot.send_chat_action(
            chat_id=message.chat_id,
            action="typing",
        )

        # Gọi Grok
        try:
            ai_response = await self.grok.analyze_alert(
                alert_text=text,
                playbook_content=playbook_content,
                category_name=category,
            )
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            await message.reply_text(
                "❌ Lỗi khi gọi Grok API. Vui lòng kiểm tra logs.",
                reply_to_message_id=message.message_id,
            )
            return

        # Format response
        header = (
            f"🔍 <b>Phân tích: {alert.alertname}</b>\n"
            f"📦 Namespace: <code>{alert.namespace}</code> | "
            f"🔴 Severity: <code>{alert.severity}</code>\n"
        )
        if category:
            header += f"📖 Playbook: <code>{category}</code>\n"
        header += "─" * 30 + "\n\n"

        full_response = header + ai_response

        # Telegram giới hạn 4096 ký tự per message
        if len(full_response) > 4096:
            full_response = full_response[:4090] + "\n..."

        sent = await message.reply_text(
            full_response,
            parse_mode="HTML",
            reply_to_message_id=message.message_id,
        )

        # Lưu vào database
        self.db.save_alert(
            alert_hash=alert_hash,
            alertname=alert.alertname,
            namespace=alert.namespace,
            severity=alert.severity,
            raw_text=text,
            ai_response=ai_response,
            message_id=sent.message_id,
        )