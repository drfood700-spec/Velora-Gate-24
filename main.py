import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update, context):
    await update.message.reply_text("أهلاً بك في متجر Velora Gate!")

async def admin_panel(update, context):
    await update.message.reply_text("أهلاً بك في لوحة التحكم.")

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "exchange":
        await query.message.edit_text("قائمة أسعار الصرف...")

def main():
    # سحب التوكن من Variables في Railway
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("خطأ: يرجى إضافة BOT_TOKEN في إعدادات Railway!")
        return

    # استخدام الطريقة الحديثة (ApplicationBuilder) بدلاً من Updater
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
