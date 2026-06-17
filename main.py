import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# إعدادات اللوغ
logging.basicConfig(level=logging.ERROR)

# تحميل الإعدادات
with open('settings.json', 'r', encoding='utf-8') as f:
    SETTINGS = json.load(f)

with open('products.json', 'r', encoding='utf-8') as f:
    PRODUCTS = json.load(f)

with open('referral.json', 'r', encoding='utf-8') as f:
    REFERRAL = json.load(f)

ADMIN_ID = SETTINGS['admin_id']
BOT_TOKEN = os.getenv('BOT_TOKEN')

# دوال مساعدة لحفظ البيانات
async def save_json(file, data):
    async with aiofiles.open(file, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))

# بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref = context.args[0] if context.args else None
    if ref and ref.isdigit() and int(ref) != user_id:
        if str(user_id) not in REFERRAL['referrals']:
            REFERRAL['referrals'][str(user_id)] = int(ref)
            REFERRAL['earnings'][str(ref)] = REFERRAL['earnings'].get(str(ref), 0) + 0  # سيتم إضافة الرصيد عند الشحن
            await save_json('referral.json', REFERRAL)

    keyboard = [
        [InlineKeyboardButton(SETTINGS['buttons']['products'], callback_data='products')],
        [InlineKeyboardButton(SETTINGS['buttons']['exchange_rate'], callback_data='rate')],
        [InlineKeyboardButton(SETTINGS['buttons']['referral'], callback_data='referral')],
        [InlineKeyboardButton(SETTINGS['buttons']['balance'], callback_data='balance')],
        [InlineKeyboardButton(SETTINGS['buttons']['recharge'], callback_data='recharge')],
        [InlineKeyboardButton(SETTINGS['buttons']['support'], callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(SETTINGS['welcome_message'], reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

# عرض المنتجات
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for product, info in PRODUCTS.items():
        if info['active']:
            keyboard.append([InlineKeyboardButton(f"{product} - {info['price_per_unit']}$", callback_data=f"buy_{product}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back")])
    await query.edit_message_text("اختر المنتج الذي ترغب في شرائه:", reply_markup=InlineKeyboardMarkup(keyboard))

# طلب العدد
async def ask_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product = query.data.replace('buy_', '')
    context.user_data['buy_product'] = product
    await query.edit_message_text(f"أدخل عدد الحسابات من {product} التي ترغب في شرائها:")

# معالجة العدد والشراء
async def process_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        quantity = int(update.message.text)
        product = context.user_data.get('buy_product')
        if not product or product not in PRODUCTS:
            await update.message.reply_text("حدث خطأ، حاول مجدداً.")
            return
        info = PRODUCTS[product]
        if quantity > info['stock']:
            await update.message.reply_text(f"❌ المخزون غير كافٍ، المتوفر {info['stock']} فقط.")
            return
        total_price = quantity * info['price_per_unit']
        # هنا يمكن إضافة منطق الخصم من الرصيد أو إتمام الدفع
        await update.message.reply_text(f"💵 السعر الإجمالي: {total_price}$\n📩 سيتم إرسال الحسابات بعد تأكيد الدفع.")
    except ValueError:
        await update.message.reply_text("⚠️ يرجى إدخال رقم صحيح.")

# سعر الصرف
async def show_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"💱 سعر الصرف الحالي: 1$ = {SETTINGS['currency_rate']} SYP")

# برنامج الإحالة
async def show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user_id}"
    earnings = REFERRAL['earnings'].get(user_id, 0)
    text = f"🎁 برنامج الإحالة\n\nرابطك الإحالة:\n{ref_link}\n\n💰 أرباحك: {earnings}$"
    await update.callback_query.edit_message_text(text)

# رصيدي
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balance_usd = 0  # سيتم جلب الرصيد من قاعدة بيانات لاحقاً
    balance_syp = balance_usd * SETTINGS['currency_rate']
    await update.callback_query.edit_message_text(f"💰 رصيدك:\n{balance_usd}$\n{balance_syp} SYP")

# شحن الرصيد
async def recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    methods = SETTINGS['payment_methods']
    text = "طرق الشحن المتاحة:\n"
    for method, detail in methods.items():
        text += f"• {method.upper()}: {detail}\n"
    text += "\nبعد الدفع، أرسل صورة الإيداع للإدمن."
    await update.callback_query.edit_message_text(text)

# تواصل مع الدعم
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(f"📞 للتواصل مع الدعم: {SETTINGS['support_contact']}")

# زر الرجوع
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# لوحة تحكم الإدمن
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    keyboard = [
        [InlineKeyboardButton("تعديل المنتجات", callback_data="edit_products")],
        [InlineKeyboardButton("تعديل سعر الصرف", callback_data="edit_rate")],
        [InlineKeyboardButton("تعديل رسالة الترحيب", callback_data="edit_welcome")],
        [InlineKeyboardButton("تعديل أزرار العميل", callback_data="edit_buttons")],
        [InlineKeyboardButton("تعديل طرق الشحن", callback_data="edit_payment")]
    ]
    await update.message.reply_text("🔧 لوحة تحكم الإدمن", reply_markup=InlineKeyboardMarkup(keyboard))

# تشغيل البوت
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_products, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(ask_quantity, pattern="^buy_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_quantity))
    app.add_handler(CallbackQueryHandler(show_rate, pattern="^rate$"))
    app.add_handler(CallbackQueryHandler(show_referral, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(show_balance, pattern="^balance$"))
    app.add_handler(CallbackQueryHandler(recharge, pattern="^recharge$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(back, pattern="^back$"))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.run_polling()
