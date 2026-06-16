import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- الدوال الخاصة بـ Velora Gate ---
async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("💰 أسعار الصرف", callback_data='exchange')],
        [InlineKeyboardButton("📦 الشحن", callback_data='shipping')],
        [InlineKeyboardButton("🛍 المنتجات", callback_data='products')],
        [InlineKeyboardButton("📞 الدعم الفني", callback_data='support')],
        [InlineKeyboardButton("📋 نظام الإحالة", callback_data='referral')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("أهلاً بك في متجر Velora Gate! اختر من القائمة:", reply_markup=reply_markup)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "exchange":
        await query.message.edit_text("نقدم أفضل أسعار الصرف لعملائنا...")
    elif query.data == "shipping":
        await query.message.edit_text("خيارات الشحن المتاحة: سريع، اقتصادي...")
    elif query.data == "products":
        await query.message.edit_text("لدينا حسابات Gmail و Apple ID و iCloud بأسعار تنافسية!")
    elif query.data == "support":
        await query.message.edit_text("تواصل مع فريق الدعم الفني عبر @SupportUser")
    elif query.data == "referral":
        await query.message.edit_text("رابط الإحالة الخاص بك يمنحك 10% من المبيعات!")
    elif query.data == "back_to_main":
        await start(query, context) # إعادة عرض القائمة الرئيسية

async def admin_panel(update, context):
    await update.message.reply_text("مرحباً بك في لوحة تحكم الأدمن لـ Velora Gate.")

# --- دالة التشغيل الأساسية ---
def main():
    # التوكن يتم سحبه من إعدادات Railway (Variables)
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("خطأ: يرجى إضافة BOT_TOKEN في إعدادات Railway!")
        return

    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Velora Gate Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
