import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

WELCOME_MESSAGE = (
    "✨ *مرحباً بك في بوابة Velora Gate الرقمية* ✨\n\n"
    "يسعدنا تلبية احتياجاتك لأرقى الحسابات والخدمات الرقمية بجودة واستقرار لا مثيل لهما.\n\n"
    "💡 *ماذا نقدم؟*\n"
    "• حسابات Apple ID و iCloud مجهزة ومؤمنة بأعلى المعايير.\n"
    "• حسابات Gmail موثقة وجاهزة للاستخدام الفوري.\n\n"
    "🚀 تصفح القائمة أدناه واكتشف الجودة الفائقة بنفسك!"
)

QUALITY_INFO = (
    "🛡️ *ضمان الجودة والأمان في Velora Gate* 🛡️\n\n"
    "🍏 *Apple ID & iCloud:*\n"
    "• استقرار عالي\n"
    "• حماية قوية\n\n"
    "📧 *Gmail:*\n"
    "• IPs نظيفة\n"
    "• موثقة\n"
)

EXCHANGE_RATE_INFO = (
    "💱 *أسعار الصرف:*\n\n"
    "• 1 USDT = 15000 SYP\n"
)

DEPOSIT_INFO = (
    "💳 *طرق الشحن*\n\n"
    "Syriatel Cash: 0912345678\n"
    "Cham Cash: 0987654321\n"
    "USDT BEP20: 0xYourWallet\n"
)

SUPPORT_INFO = "🤝 *الدعم الفني*"

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    back = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ رجوع", callback_data="main")]
    ])

    if data == "main":
        await query.edit_message_text(WELCOME_MESSAGE, reply_markup=main_menu(), parse_mode="Markdown")

    elif data == "quality":
        await query.edit_message_text(QUALITY_INFO, reply_markup=back, parse_mode="Markdown")

    elif data == "exchange":
        await query.edit_message_text(EXCHANGE_RATE_INFO, reply_markup=back)

    elif data == "deposit":
        await query.edit_message_text(DEPOSIT_INFO, reply_markup=back)

    elif data == "support":
        await query.edit_message_text(SUPPORT_INFO, reply_markup=back)

    elif data == "products":
        await query.edit_message_text(
            "📦 المنتجات:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Apple ID", callback_data="apple")],
                [InlineKeyboardButton("Gmail", callback_data="gmail")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="main")]
            ])
        )

    elif data in ["apple", "gmail"]:
        await query.edit_message_text(
            f"📦 قسم {data}",
            reply_markup=back
        )

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()