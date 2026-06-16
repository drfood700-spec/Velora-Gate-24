import json
import os
from telegram.ext import ApplicationBuilder, CommandHandler

ADMIN_ID = 7977349795

# دالة قراءة الإعدادات
def load_settings():
    with open('settings.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def start(update, context):
    settings = load_settings()
    await update.message.reply_text(settings['welcome_message'])

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    settings = load_settings()
    msg = (f"🛠 لوحة التحكم - Velora Gate\n"
           f"💰 سعر الصرف الحالي: {settings['exchange_rate']}\n"
           f"🍎 سعر iCloud: {settings['prices']['icloud']}\n"
           f"📧 سعر Gmail: {settings['prices']['gmail']}")
    await update.message.reply_text(msg)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.run_polling()

if __name__ == '__main__':
    main()
