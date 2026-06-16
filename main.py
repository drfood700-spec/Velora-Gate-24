import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

ADMIN_ID = 7977349795
# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- الدوال الخاصة بمتجرك ---
async def start(update, context):
    await update.message.reply_text("أهلاً بك في Velora Gate!")

async def admin_panel(update, context):
    await update.message.reply_text("مرحباً بك في لوحة التحكم.")

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    # هنا تم دمج المنطق الذي كان في صورك السابقة
    if query.data == "exchange":
        await query.message.edit_text("قائمة أسعار الصرف...")
    elif query.data == "shipping":
        await query.message.edit_text("معلومات الشحن...")
    elif query.data == "products":
        await query.message.edit_text("المنتجات المتاحة حالياً: Apple ID...")
    elif query.data == "support":
        await query.message.edit_text("تواصل مع الدعم الفني لـ Velora Gate مباشرة")
    elif query.data == "back_to_main":
        await query.message.edit_text("أهلاً بك في القائمة الرئيسية.")

# --- دالة التشغيل ---
def main():
    # ضع التوكن الخاص بك هنا بين علامتي التنصيص
    TOKEN = "8995974815:AAERR9AP_O6EFW5a_KLGQyNck1ovQflzTfs"
    
    application = Application.builder().token(TOKEN).build()
    
    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is starting now...")
    application.run_polling()

if __name__ == '__main__':
    main()
