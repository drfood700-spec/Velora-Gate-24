import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- الإعدادات الأساسية ---
BOT_TOKEN = "8995974815:AAHKBXwgOtRFJ1bKUkQAMMms4r5V6UMjwaEA"

# قائمة المعرفات المسموح لها بدخول لوحة التحكم (تضمن عدم حدوث أي خطأ في النوع)
ADMIN_IDS = [7977349795, "7977349795"]  

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- النصوص والبيانات المخزنة مؤقتاً (يمكن تعديلها من اللوحة) ---
DATA = {
    "welcome": (
        "✨ *مرحباً بك في بوابة Velora Gate الرقمية* ✨\n\n"
        "يسعدنا تلبية احتياجاتك لأرقى الحسابات والخدمات الرقمية بجودة واستقرار لا مثيل لهما.\n\n"
        "💡 *ماذا نقدم؟*\n"
        "• حسابات Apple ID و iCloud مجهزة ومؤمنة بأعلى المعايير.\n"
        "• حسابات Gmail موثقة وجاهزة للاستخدام الفوري.\n\n"
        "🚀 تصفح القائمة أدناه واكتشف الجودة الفائقة بنفسك!"
    ),
    "quality": (
        "🛡️ *ضمان الجودة والأمان في Velora Gate* 🛡️\n\n"
        "🍏 *Apple ID & iCloud:*\n"
        "• استقرار عالي\n"
        "• حماية قوية\n\n"
        "📧 *Gmail:*\n"
        "• IPs نظيفة\n"
        "• موثقة\n"
    ),
    "exchange": "💱 *أسعار الصرف:*\n\n• 1 USDT = 15000 SYP\n",
    "deposit": "💳 *طرق الشحن*\n\nSyriatel Cash: 0912345678\nCham Cash: 0987654321\nUSDT BEP20: 0xYourWallet\n",
    "support": "🤝 *الدعم الفني*"
}

# قائمة لتخزين المستخدمين لإرسال الإذاعة (تتحدث تلقائياً عند ضغط start)
USERS = set()

# --- القوائم والأزرار ---
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ منتجاتنا", callback_data="products")],
        [
            InlineKeyboardButton("💳 شحن", callback_data="deposit"),
            InlineKeyboardButton("💱 سعر الصرف", callback_data="exchange")
        ],
        [
            InlineKeyboardButton("🌟 جودة", callback_data="quality"),
            InlineKeyboardButton("🤝 دعم", callback_data="support")
        ]
    ])

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 تعديل سعر الصرف", callback_data="edit_exchange")],
        [InlineKeyboardButton("📝 تعديل طرق الشحن", callback_data="edit_deposit")],
        [InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats")],
        [InlineKeyboardButton("⬅️ خروج من اللوحة", callback_data="main")]
    ])

# --- الأوامر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.from_user:
        USERS.add(update.message.from_user.id)
        
    await update.message.reply_text(
        DATA["welcome"],
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # التحقق من أن المرسل في قائمة الأدمن
    if user_id in ADMIN_IDS:
        await update.message.reply_text(
            "⚙️ **مرحباً بك في لوحة تحكم الإدارة لـ Velora Gate**\n\nاختر من الأزرار أدناه للتحكم بالبوت:",
            reply_markup=admin_menu(),
            parse_mode="Markdown"
        )
    else:
        # رسالة كاشفة لمعرفة الرقم والنوع المسجل في السيرفر
        await update.message.reply_text(f"❌ عذراً، هذا الأمر مخصص للإدارة فقط.\nرقم حسابك الذي قرأه السيرفر هو: `{user_id}`", parse_mode="Markdown")

# --- معالج الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    back = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="main")]])
    admin_back = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ عودة للوحة", callback_data="admin_home")]])

    # تحديث قائمة المستخدمين عند التفاعل
    USERS.add(user_id)

    # --- أزرار المستخدمين ---
    if data == "main":
        await query.edit_message_text(DATA["welcome"], reply_markup=main_menu(), parse_mode="Markdown")
    elif data == "quality":
        await query.edit_message_text(DATA["quality"], reply_markup=back, parse_mode="Markdown")
    elif data == "exchange":
        await query.edit_message_text(DATA["exchange"], reply_markup=back, parse_mode="Markdown")
    elif data == "deposit":
        await query.edit_message_text(DATA["deposit"], reply_markup=back, parse_mode="Markdown")
    elif data == "support":
        await query.edit_message_text(DATA["support"], reply_markup=back, parse_mode="Markdown")
    elif data == "products":
        await query.edit_message_text(
            "📦 المنتجات المتاحة حالياً:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Apple ID & iCloud", callback_data="apple")],
                [InlineKeyboardButton("Gmail Accounts", callback_data="gmail")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="main")]
            ])
        )
    elif data in ["apple", "gmail"]:
        await query.edit_message_text(f"📦 **قسم {data.upper()}**\n\nسيتم إضافة الأسعار والحسابات المتوفرة هنا قريباً.", reply_markup=back, parse_mode="Markdown")

    # --- أزرار لوحة التحكم (الأدمن فقط) ---
    elif data == "admin_home" and user_id == ADMIN_ID:
        await query.edit_message_text("⚙️ **لوحة التحكم:**", reply_markup=admin_menu(), parse_mode="Markdown")
        
    elif data == "admin_stats" and user_id == ADMIN_ID:
        await query.edit_message_text(f"📊 **إحصائيات المتجر:**\n\n👥 عدد المشتركين النشطين منذ التشغيل: {len(USERS)} مستخدم.", reply_markup=admin_back, parse_mode="Markdown")
        
    elif data == "edit_exchange" and user_id == ADMIN_ID:
        context.user_data["waiting_for_input"] = "exchange"
        await query.edit_message_text("📝 أرسل الآن النص الجديد لأسعار الصرف (رسالة نصية عادية):", reply_markup=admin_back)
        
    elif data == "edit_deposit" and user_id == ADMIN_ID:
        context.user_data["waiting_for_input"] = "deposit"
        await query.edit_message_text("📝 أرسل الآن النص الجديد لطرق الشحن وحساباتك المعتمدة:", reply_markup=admin_back)

# --- معالج الرسائل النصية للتحديث والإدخال ---
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # التحقق من أن المستخدم أدمن وفي حالة انتظار إدخال بيانات
    if user_id == ADMIN_ID and "waiting_for_input" in context.user_data:
        target = context.user_data["waiting_for_input"]
        DATA[target] = update.message.text # تحديث البيانات فوراً
        del context.user_data["waiting_for_input"] # إنهاء حالة الانتظار
        
        await update.message.reply_text(
            "✅ تم تحديث البيانات بنجاح في النظام وستظهر للعملاء فوراً!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠️ العودة للوحة التحكم", callback_data="admin_home")]])
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel)) # أمر الدخول للوحة التحكم
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # معالج الرسائل النصية لتحديث لوحة التحكم
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot with Admin Panel running on Railway...")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
