import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# دالة تحميل البيانات
def get_data():
    with open('settings.json', 'r', encoding='utf-8') as f: return json.load(f)

async def start(update, context):
    data = get_data()
    # نظام إحصائيات بسيط (زيادة عدد الزوار)
    data['stats']['visitors'] += 1
    with open('settings.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
    
    await update.message.reply_text(data['bot_config']['welcome_msg'])

async def admin_panel(update, context):
    if update.effective_user.id != 7977349795: return
    
    keyboard = [
        [InlineKeyboardButton("📝 تعديل سعر الصرف", callback_data='edit_rate')],
        [InlineKeyboardButton("📦 تعديل طرق الشحن", callback_data='edit_shipping')],
        [InlineKeyboardButton("📊 إحصائيات البوت", callback_data='show_stats')],
        [InlineKeyboardButton("💬 تعديل الدعم الفني", callback_data='edit_support')]
    ]
    await update.message.reply_text("🛠 أهلاً بك في لوحة تحكم Velora Gate:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = get_data()
    
    if query.data == 'show_stats':
        msg = f"📊 إحصائيات البوت:\nعدد الزوار: {data['stats']['visitors']}"
        await query.message.edit_text(msg)
    # هنا ستضيف باقي المنطق لكل زر...

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", admin_panel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
