import logging
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- الدوال الخاصة بك (يجب أن تكون معرفة هنا) ---
async def start(update, context):
    await update.message.reply_text("أهلاً بك في متجر Velora Gate!")

async def admin_panel(update, context):
    await update.message.reply_text("أهلاً بك في لوحة التحكم.")

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    # هنا تضع منطق الأزرار الخاص بك
    if query.data == "exchange":
        await query.message.edit_text("قائمة أسعار الصرف...")
    elif query.data == "back_to_main":
        await query.message.edit_text("الرئيسية")

# --- تعريف دالة الـ main ---
def main():
    # استخدام التوكن من المتغيرات في Railway
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN في المتغيرات!")
        return

    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is starting now...")
    application.run_polling()

# --- التشغيل النهائي ---
if __name__ == '__main__':
    main()
