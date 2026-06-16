import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# إعداد السجلات لنعرف سبب أي مشكلة في الـ Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def start(update, context):
    update.message.reply_text("مرحباً بك! البوت يعمل الآن بنجاح.")

def main():
    # سحب التوكن من إعدادات Railway
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("خطأ: يرجى التأكد من إضافة BOT_TOKEN في تبويب Variables في Railway")
        return

    # إنشاء التطبيق
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة أمر البداية
    application.add_handler(CommandHandler("start", start))
    
    print("البوت يعمل الآن، بانتظار الأوامر...")
    
    # تشغيل البوت
    application.run_polling()

if __name__ == '__main__':
    main()
