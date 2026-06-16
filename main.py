import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- الإعدادات الأساسية ---
BOT_TOKEN = "8995974815:AAEER9AP_O6EFW5a_KLGl6D-Vb7R_5vP1Ag"

# قائمة المعرفات المسموح لها بدخول لوحة التحكم (نصوص وأرقام)
ADMIN_IDS = ["7977349795", 7977349795, "0"]  

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- النصوص والبيانات المخزنة مؤقتاً ---
DATA = {
    "welcome": (
        "✨ *مرحباً بك في بوابة Velora Gate الرقمية* ✨\n\n"
        "يسعدنا تلبية احتياجاتك لأرقى الحسابات والخدمات الرقمية بجودة واستقرار لا مثيل لهما!\n\n"
        "💡 *ماذا نقدم؟*\n"
        "• حسابات Apple ID و iCloud مجهزة ومؤمنة بأعلى المعايير.\n"
        "• حسابات Gmail موثقة وجاهزة للاستخدام الفوري.\n\n"
        "🚀 *تصفح القائمة أدناه واكتشف الجودة الفائقة بنفسك!*"
    ),
    "quality": (
        "🛡️ *ضمان الجودة والأمان في Velora Gate* 🛡️\n\n"
        "🍏 *Apple ID & iCloud:*\n"
        "• حسابات شخصية جديدة كلياً وغير مستخدمة من قبل.\n"
        "• مؤمنة بأسئلة أمان مخصصة وإيميل إنقاذ خاص بك.\n"
        "• ضمان كامل ضد الإغلاق المفاجئ مع دعم التحديث المستمر.\n\n"
        "📧 *حسابات Gmail:*\n"
        "• حسابات منشأة بـ IPs نظيفة وموثقة برقم هاتف (تم إزالته بعد التفعيل).\n"
        "• تدعم تشغيل الإعلانات، القنوات، والخدمات الحساسة بدون مشاكل.\n"
        "• تشمل تفاصيل الدخول الكاملة مع إيميل استرداد مفعل."
    ),
    "shipping": (
        "⚡ *طرق الشحن والتسليم السريع* ⚡\n\n"
        "• **التسليم الفوري:** الحسابات الجاهزة يتم إرسال بياناتها لك تلقائياً داخل البوت بمجرد تأكيد الدفع.\n"
        "• **الطلبات الخاصة:** تستغرق من 5 إلى 30 دقيقة كحد أقصى وفريقنا يتابع معك خطوة بخطوة.\n\n"
        "💰 *طرق الدفع المتوفرة حالياً:* (يمكنك التنسيق مع الدعم الفني لتسهيل معاملتك)."
    ),
    "exchange_rate": "💵 **سعر الصرف الحالي المعتمد في المتجر:**\n\n• 1 دولار رقمي = 1.00 USDT\n• لمعرفة الأسعار بالعملات المحلية، يرجى التواصل مع الإدارة مباشرة."
}

# --- لوحات المفاتيح (الأزرار) ---
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🛍️ منتجاتنا", callback_data="products")],
        [InlineKeyboardButton("💹 سعر الصرف", callback_data="exchange"), InlineKeyboardButton("💳 شحن", callback_data="shipping")],
        [InlineKeyboardButton("🌟 جودة", callback_data="quality"), InlineKeyboardButton("🤝 دعم", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu():
    keyboard = [
        [InlineKeyboardButton("📝 تعديل سعر الصرف", callback_data="edit_exchange")],
        [InlineKeyboardButton("🚚 تعديل طرق الشحن", callback_data="edit_shipping")],
        [InlineKeyboardButton("📊 إحصائيات البوت", callback_data="bot_stats")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- الأوامر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.from_user:
        await update.message.reply_text(
            DATA["welcome"],
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return
        
    user_id = update.message.from_user.id
    
    # فحص شامل وصارم يقبل الدخول إذا طابق الـ ID بأي شكل
    if str(user_id) in [str(adm) for adm in ADMIN_IDS] or user_id == 7977349795 or str(user_id) == "7977349795":
        await update.message.reply_text(
            "⚙️ **مرحباً بك في لوحة تحكم الإدارة لـ Velora Gate**\n\nاختر من الأزرار أدناه للتحكم بالبوت:",
            reply_markup=admin_menu(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ عذراً، هذا الأمر مخصص للإدارة فقط.\nرقم حسابك الحالي: `{user_id}`", 
            parse_mode="Markdown"
        )

# --- معالج الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    
    if query.data == "exchange":
        await query.message.edit_text(DATA["exchange_rate"], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الخلف", callback_data="back_to_main")]]), parse_mode="Markdown")
    elif query.data == "shipping":
        await query.message.edit_text(DATA["shipping"], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الخلف", callback_data="back_to_main")]]), parse_mode="Markdown")
    elif query.data == "quality":
        await query.message.edit_text(DATA["quality"], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الخلف", callback_data="back_to_main")]]), parse_mode="Markdown")
    elif query.data == "support":
        await query.message.edit_text("🤝 **الدعم الفني لـ Velora Gate:**\n\nلأي استفسار أو مشكلة، تواصل مباشرة مع الإدارة: @Velora_Admin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الخلف", callback_data="back_to_main")]]), parse_mode="Markdown")
    elif query.data == "products":
        await query.message.edit_text("🛍️ **المنتجات المتاحة حالياً:**\n\n• حسابات Apple ID مميزة\n• حسابات iCloud مؤمنة\n• حسابات Gmail موثقة\n\n(لطلب أي حساب، تواصل مع الدعم الفني حالياً لحين تفعيل الدفع التلقائي).", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الخلف", callback_data="back_to_main")]]), parse_mode="Markdown")
    elif query.data == "back_to_main":
        await query.message.edit_text(DATA["welcome"], reply_markup=main_menu(), parse_mode="Markdown")
    elif query.data in ["edit_exchange", "edit_shipping", "bot_stats"]:
        await query.message.reply_text("🚧 هذه الميزة مخصصة للربط مع قاعدة البيانات وقيد التطوير حالياً.")

# --- التشغيل الأساسي ---
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling()

if __name__ == '__main__':
    main()
