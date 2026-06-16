import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

ADMIN_ID = 7977349795

def load_data():
    if not os.path.exists('settings.json'):
        return {"bot_config": {"welcome_msg": "مرحباً!", "exchange_rate": 15000}, "inventory": {"icloud": {"price": 5, "stock": 0}, "gmail": {"price": 2, "stock": 0}}}
    with open('settings.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def start(update, context):
    data = load_data()
    await update.message.reply_text(data['bot_config']['welcome_msg'], parse_mode='Markdown')

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    data = load_data()
    msg = (f"⚙️ *لوحة تحكم Velora Gate*\n\n"
           f"💰 سعر الصرف: `{data['bot_config']['exchange_rate']}`\n"
           f"🍎 iCloud: `{data['inventory']['icloud']['price']}$` | المخزون: `{data['inventory']['icloud']['stock']}`\n"
           f"📧 Gmail: `{data['inventory']['gmail']['price']}$` | المخزون: `{data['inventory']['gmail']['stock']}`")
    
    keyboard = [[InlineKeyboardButton("🍎 تحديث iCloud", callback_data='up_icloud'), InlineKeyboardButton("📧 تحديث Gmail", callback_data='up_gmail')]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'up_icloud':
        await query.message.reply_text("أرسل الرقم الجديد لمخزون iCloud:")
        context.user_data['action'] = 'set_icloud'

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", admin_panel))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("البوت يعمل...")
    app.run_polling()

if __name__ == '__main__':
    main()
