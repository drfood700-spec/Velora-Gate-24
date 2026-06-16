import logging
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update, context):
    await update.message.reply_text("تم تشغيل البوت بنجاح! مرحباً بك في Velora Gate.")

async def admin_panel(update, context):
    await update.message.reply_text("لوحة التحكم تعمل.")

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

def main():
    # التأكد من التوكن
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("ERROR: BOT_TOKEN not found!")
        return

    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("panel", admin_panel))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        print("Velora Gate Bot is now running...")
        application.run_polling()
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == '__main__':
    main()
