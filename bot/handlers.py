import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .parser import parse_alert_message
from .playbook_loader import PlaybookLoader
from .groq_client import GroqClient


logger = logging.getLogger(__name__)

class AlertHandler:
    def __init__(
        self,
        playbook_loader: PlaybookLoader,
        groq_client: GroqClient,
        bot_username: str,
    ):
        self.playbooks = playbook_loader
        self.groq = groq_client
        self.bot_username = bot_username.lstrip("@")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message

        if not message or not message.text:
            return

        text = message.text

        logger.info(f"Received message from chat_id={message.chat_id}, text={text[:50]}")

        # Chỉ xử lý khi được mention
        mention = f"@{self.bot_username}"
        if mention not in text:
            return

        # Parse alert
        alert = parse_alert_message(text)
        if not alert:
            logger.info("Message có mention nhưng không phải alert, bỏ qua.")
            return

        # Load playbook
        category, playbook_content = self.playbooks.get_for_alert(alert.alertname)

        # Typing indicator
        await context.bot.send_chat_action(
            chat_id=message.chat_id,
            action="typing",
        )

        # Gọi Groq API
        try:
            ai_response = await self.groq.analyze_alert(
                alert_text=text,
                playbook_content=playbook_content,
                category_name=category,
            )
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            await message.reply_text(
                "❌ Lỗi khi gọi Groq API. Vui lòng kiểm tra logs.",
                reply_to_message_id=message.message_id,
            )
            return

        # Format header (HTML)
        header = (
            f"🔍 <b>Phân tích: {alert.alertname}</b>\n"
            f"📦 Namespace: <code>{alert.namespace}</code> | "
            f"🔴 Severity: <code>{alert.severity}</code>\n"
        )
        if category:
            header += f"📖 Playbook: <code>{category}</code>\n"
        header += "─" * 30 + "\n\n"

        # Gửi header trước (HTML format)
        await message.reply_text(
            header,
            parse_mode="HTML",
            reply_to_message_id=message.message_id,
        )

        # Truncate response nếu quá dài
        if len(ai_response) > 4096:
            ai_response = ai_response[:4090] + "\n..."

        # Gửi content (Markdown format - giữ nguyên markdown từ Groq)
        try:
            await message.reply_text(
                ai_response,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_to_message_id=message.message_id,
            )
        except Exception as e:
            logger.warning(f"Failed to send with MARKDOWN_V2, falling back to plain text: {e}")
            # Nếu MarkdownV2 fail, gửi dạng plain text
            await message.reply_text(
                ai_response,
                reply_to_message_id=message.message_id,
            )
