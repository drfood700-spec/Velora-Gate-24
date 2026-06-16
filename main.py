import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler

ADMIN_ID = 7977349795

def load_data():
    with open('settings.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def start(update, context):
    data = load_data()
    # الرسالة الترحيبية بتنسيق احترافي
    await update.message.reply_text(data['bot_config']['welcome_msg'], parse_mode='Markdown')

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    
    data = load_data()
    msg = (f"⚙️ *لوحة تحكم Velora Gate*\n\n"
           f"💰 سعر الصرف: `{data['bot_config']['exchange_rate']}`\n\n"
           f"🍎 iCloud: `{data['inventory']['icloud']['price']}$` | المخزون: `{data['inventory']['icloud']['stock']}`\n"
           f"📧 Gmail: `{data['inventory']['gmail']['price']}$` | المخزون: `{data['inventory']['gmail']['stock']}`")
    
    await update.message.reply_text(msg, parse_mode='Markdown')

# ... تابع إضافة باقي الدوال ...
