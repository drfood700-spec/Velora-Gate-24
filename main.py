import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

ADMIN_ID = 7977349795

def get_data():
    with open('settings.json', 'r', encoding='utf-8') as f: return json.load(f)

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    data = get_data()
    # الأزرار هنا تقرأ الأسماء من ملف الإعدادات
    btns = data['buttons']
    keyboard = [
        [InlineKeyboardButton(btns['btn1'], callback_data='edit_rate')],
        [InlineKeyboardButton(btns['btn2'], callback_data='edit_shipping')],
        [InlineKeyboardButton(btns['btn3'], callback_data='show_stats')]
    ]
    await update.message.reply_text(data['bot_config']['panel_title'], reply_markup=InlineKeyboardMarkup(keyboard))

# دالة التعامل مع الأزرار العامة
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = get_data()
    # هنا المنطق الخاص بكل زر...
    if query.data == 'show_stats':
        await query.message.edit_text(f"📊 {data['stats_text']}")

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("panel", admin_panel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__': main()
