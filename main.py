import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد السجلات (Logs)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# جلب توكن البوت من بيئة التشغيل
BOT_TOKEN = os.getenv("BOT_TOKEN")

# المعرف الخاص بك كمسؤول
ADMIN_IDS = [7977349795]

# نصوص القوائم والبيانات
DATA = {
    "welcome": (
        "✨ **مرحباً بك في بوابة Velora Gate الرقمية** ✨\n\n"
        "يسعدنا تلبية احتياجاتك لأرقى الحسابات والخدمات الرقمية بجودة واستقرار لا مثيل لهما!\n\n"
        "💡 **ماذا نقدم؟**\n"
        "• حسابات Apple ID و iCloud مجهزة ومؤمنة بأعلى المعايير.\n"
        "• حسابات Gmail موثقة وجاهزة للاستخدام الفوري.\n\n"
        "🚀 تصفح القائمة أدناه واكتشف الجودة الفائقة بنفسك!"
    ),
    "exchange_rate": "💹 **سعر الصرف الحالي:**\n\nالدفع متوفر حالياً عبر العملات الرقمية (USDT - BEP20).",
    "shipping": "💳 **طرق الشحن المتوفرة:**\n\nيمكنك الشحن تلقائياً باستخدام محفظة Cwallet لشبكة BEP20.",
    "quality": "🌟 **ضمان الجودة:**\n\nجميع حساباتنا مضمونة وموثقة وتخضع لأعلى معايير الأمان.",
}

# لوحة مفاتيح القائمة الرئيسية (تم إضافة زر الإحالة)
main_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛍️ منتجاتنا", callback_data="products")],
    [InlineKeyboardButton("💹 سعر الصرف", callback_data="exchange"), InlineKeyboardButton("💳 شحن", callback_data="shipping")],
    [InlineKeyboardButton("👥 نظام الإحالة (كسب رصيد)", callback_data="referral")],
    [InlineKeyboardButton("🌟 جودة", callback_data="quality"), InlineKeyboardButton("🤝 دعم", callback_data="support")]
])

# لوحة مفاتيح الإدارة (Admin Panel)
admin_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("📝 تعديل سعر الصرف", callback_data="edit_exchange")],
    [InlineKeyboardButton("📦 تعديل طرق الشحن", callback_data="edit_shipping")],
    [InlineKeyboardButton("📊 إحصائيات البوت", callback_data="bot_stats")],
    [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="back_to_main")]
])

# زر العودة للقائمة الرئيسية للزبائن
back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ عودة", callback_data="back_to_main")]])

# --- معالجة الأوامر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id
    
    # فحص إذا كان المستخدم دخل عبر رابط إحالة شخص آخر
    if args and args[0].startswith("ref_"):
        referrer_id = args[0].replace("ref_", "")
        # تنبيه برمجياً في الـ Logs (سيتم ربطها بالكامل بقاعدة البيانات بعد امتحاناتك)
        logging.info(f"المستخدم {user_id} دخل عن طريق إحالة من الحساب: {referrer_id}")
        
    await update.message.reply_text(DATA["welcome"], reply_markup=main_menu, parse_mode="Markdown")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        await update.message.reply_text("🛠️ **أهلاً بك في لوحة تحكم الإدارة لـ Velora Gate:**", reply_markup=admin_menu, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ عذراً، هذا الأمر مخصص للإدارة فقط.\nرقم حسابك الحالي: `{user_id}`", parse_mode="Markdown")

# --- معالج الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()

    user_id = query.from_user.id
    bot_username = context.bot.username

    if query.data == "exchange":
        await query.message.edit_text(DATA["exchange_rate"], reply_markup=back_markup, parse_mode="Markdown")
    elif query.data == "shipping":
        await query.message.edit_text(DATA["shipping"], reply_markup=back_markup, parse_mode="Markdown")
    elif query.data == "quality":
        await query.message.edit_text(DATA["quality"], reply_markup=back_markup, parse_mode="Markdown")
    elif query.data == "support":
        await query.message.edit_text("🤝 **الدعم الفني لـ Velora Gate:**\n\nللإستفسار أو مواجهة أي مشكلة، تواصل مع الإدارة مباشرة.", reply_markup=back_markup, parse_mode="Markdown")
    elif query.data == "products":
        await query.message.edit_text("🛍️ **المنتجات المتاحة حالياً:**\n\n• حسابات Apple ID\n• حسابات iCloud\n• حسابات Gmail", reply_markup=back_markup, parse_mode="Markdown")
    
    elif query.data == "referral":
        # توليد رابط إحالة حقيقي لكل مستخدم بناءً على الـ ID الخاص به
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        ref_text = (
            "👥 **نظام الإحالة كسب 10% رصيد مجاني!**\n\n"
            "شارك رابط الإحالة الخاص بك مع أصدقائك، وعند قيام أي شخص بالشحن عن طريقك، ستكسب فوراً **10%** من قيمة شحنه تضاف إلى رصيدك تلقائياً!\n\n"
            f"🔗 **رابط الإحالة الفريد الخاص بك:**\n`{ref_link}`\n\n"
            "انقر على الرابط أعلاه لنسخه ومشاركته فوراً!"
        )
        await query.message.edit_text(ref_text, reply_markup=back_markup, parse_mode="Markdown")
        
    elif query.data == "back_to_main":
        await query.message.edit_text(DATA["welcome"], reply_markup=main_menu, parse_mode="Markdown")
    elif query.data in ["edit_exchange", "edit_shipping", "bot_stats"]:
        await query.message.reply_text("🚧 هذه الميزة قيد التطوير حالياً للربط مع قاعدة البيانات.")

# --- التشغيل الأساسي ---
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling()

if __name__ == '__main__':
    main()
