import asyncio
import logging
import random
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    BotCommand,
    User,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    AIORateLimiter,
)

# ---------------------- Configuration ----------------------
BOT_TOKEN = "8995974815:AAERR9AP_O6EFW5a_KLGQyNck1ovQflzTfs"
ADMIN_ID = 7977349795  # أيدي الأدمن

# حالات المحادثة
(
    SELECTING_PRODUCT,
    SELECTING_ACTION,
    TYPING_REPLY,
    TYPING_USER_ID,
    TYPING_AMOUNT,
    TYPING_EXCHANGE_RATE,
    TYPING_PRODUCT_NAME,
    TYPING_PRODUCT_PRICE,
    TYPING_PRODUCT_STOCK,
    CONFIRM_DELETE,
) = range(10)

# ---------------------- Database Setup ----------------------
def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    # جدول المنتجات
    c.execute(
        """CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  price REAL NOT NULL,
                  stock INTEGER NOT NULL,
                  type TEXT NOT NULL)"""
    )
    # جدول المستخدمين
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  referrer_id INTEGER,
                  balance REAL DEFAULT 0,
                  registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )
    # جدول الإحالات
    c.execute(
        """CREATE TABLE IF NOT EXISTS referrals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  referrer_id INTEGER,
                  referred_id INTEGER,
                  bonus REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )
    # جدول سعر الصرف
    c.execute(
        """CREATE TABLE IF NOT EXISTS exchange_rate
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  currency TEXT NOT NULL,
                  rate REAL NOT NULL,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )
    # جدول إحصائيات الزوار
    c.execute(
        """CREATE TABLE IF NOT EXISTS visitors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )
    # جدول سجل العمليات
    c.execute(
        """CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  product_id INTEGER,
                  quantity INTEGER,
                  total REAL,
                  status TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )
    conn.commit()
    conn.close()

def get_products_by_type(product_type: str) -> List[Tuple]:
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "SELECT id, name, price, stock FROM products WHERE type=? AND stock>0",
        (product_type,),
    )
    products = c.fetchall()
    conn.close()
    return products

def get_all_products() -> List[Tuple]:
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock, type FROM products")
    products = c.fetchall()
    conn.close()
    return products

def get_exchange_rates() -> Dict:
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT currency, rate FROM exchange_rate")
    rates = c.fetchall()
    conn.close()
    return {currency: rate for currency, rate in rates}

def update_exchange_rate(currency: str, rate: float):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO exchange_rate (currency, rate, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (currency, rate),
    )
    conn.commit()
    conn.close()

def add_product(name: str, price: float, stock: int, type: str):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO products (name, price, stock, type) VALUES (?, ?, ?, ?)",
        (name, price, stock, type),
    )
    conn.commit()
    conn.close()

def update_product(product_id: int, name: str, price: float, stock: int):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "UPDATE products SET name=?, price=?, stock=? WHERE id=?",
        (name, price, stock, product_id),
    )
    conn.commit()
    conn.close()

def delete_product(product_id: int):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def register_user(user: User, referrer_id: Optional[int] = None):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (id, username, first_name, last_name, referrer_id) VALUES (?, ?, ?, ?, ?)",
        (user.id, user.username, user.first_name, user.last_name, referrer_id),
    )
    if referrer_id:
        # إضافة مكافأة الإحالة للمُحيل (10% من قيمة شحن المستخدم الجديد)
        # سيتم تحديثها عند إتمام عملية الشحن
        pass
    conn.commit()
    conn.close()

def log_visitor(user_id: int):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO visitors (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_stats() -> Dict:
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    # عدد الزوار اليوم
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(DISTINCT user_id) FROM visitors WHERE DATE(visited_at)=?", (today,))
    today_visitors = c.fetchone()[0] or 0
    # إجمالي الزوار
    c.execute("SELECT COUNT(DISTINCT user_id) FROM visitors")
    total_visitors = c.fetchone()[0] or 0
    # عدد المستخدمين
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0] or 0
    conn.close()
    return {
        "today_visitors": today_visitors,
        "total_visitors": total_visitors,
        "total_users": total_users,
    }

def add_balance(user_id: int, amount: float):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id: int) -> float:
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_referrals(user_id: int) -> List[Tuple]:
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "SELECT referred_id, bonus, created_at FROM referrals WHERE referrer_id=?",
        (user_id,),
    )
    referrals = c.fetchall()
    conn.close()
    return referrals

def add_referral_bonus(referrer_id: int, referred_id: int, amount: float):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    bonus = amount * 0.1  # 10%
    c.execute(
        "INSERT INTO referrals (referrer_id, referred_id, bonus) VALUES (?, ?, ?)",
        (referrer_id, referred_id, bonus),
    )
    c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (bonus, referrer_id))
    conn.commit()
    conn.close()

# ---------------------- Keyboard Functions ----------------------
def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("💱 سعر الصرف", callback_data="exchange_rate")],
        [InlineKeyboardButton("📦 منتجاتنا", callback_data="products")],
        [InlineKeyboardButton("💰 شحن رصيدي", callback_data="recharge")],
        [InlineKeyboardButton("👤 التواصل مع الدعم", callback_data="support")],
        [InlineKeyboardButton("👥 نظام الإحالة", callback_data="referral")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_products_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🍎 Apple ID", callback_data="product_apple")],
        [InlineKeyboardButton("📧 Gmail Account", callback_data="product_gmail")],
        [InlineKeyboardButton("☁️ iCloud Account", callback_data="product_icloud")],
        [InlineKeyboardButton("🔙 الرجوع", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📊 الاحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("💱 تعديل سعر الصرف", callback_data="admin_exchange")],
        [InlineKeyboardButton("📦 تعديل المنتجات", callback_data="admin_products")],
        [InlineKeyboardButton("➕ إضافة منتج", callback_data="admin_add_product")],
        [InlineKeyboardButton("📨 إرسال رسالة للجميع", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 الرجوع", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_product_action_keyboard(product_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🛒 شراء", callback_data=f"buy_{product_id}")],
        [InlineKeyboardButton("🔙 الرجوع للمنتجات", callback_data="products")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("✏️ تعديل", callback_data=f"edit_product_{product_id}")],
        [InlineKeyboardButton("🗑 حذف", callback_data=f"delete_product_{product_id}")],
        [InlineKeyboardButton("🔙 الرجوع", callback_data="admin_products")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------- Message Handlers ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    # تسجيل الزائر
    log_visitor(user.id)

    # تسجيل المستخدم إذا لم يكن مسجلاً
    register_user(user)

    # التحقق من وجود إحالة
    args = context.args
    referrer_id = None
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id != user.id:  # منع الإحالة الذاتية
            register_user(user, referrer_id)

    # رسالة الترحيب
    welcome_text = (
        f"👋 مرحباً {user.first_name}!\n\n"
        "🛒 مرحباً بك في متجرنا الإلكتروني!\n"
        "نقدم لك أفضل الخدمات بأسعار منافسة.\n\n"
        "اختر الخدمة التي تريدها من الأزرار أدناه:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    data = query.data
    log_visitor(user.id)

    if data == "back_main":
        await query.edit_message_text(
            "🏠 القائمة الرئيسية:\nاختر الخدمة التي تريدها:",
            reply_markup=get_main_keyboard(),
        )

    elif data == "exchange_rate":
        rates = get_exchange_rates()
        text = "💱 **أسعار الصرف الحالية:**\n\n"
        if rates:
            for currency, rate in rates.items():
                text += f"• {currency}: {rate} $\n"
        else:
            text += "⚠️ لا توجد أسعار صرف مسجلة حالياً."
        await query.edit_message_text(text, parse_mode="Markdown")

    elif data == "products":
        await query.edit_message_text(
            "📦 **اختر نوع المنتج:**", parse_mode="Markdown", reply_markup=get_products_keyboard()
        )

    elif data.startswith("product_"):
        product_type = data.replace("product_", "")
        type_map = {"apple": "Apple ID", "gmail": "Gmail", "icloud": "iCloud"}
        product_type_display = type_map.get(product_type, product_type)
        products = get_products_by_type(product_type)
        if products:
            text = f"📦 **منتجات {product_type_display}:**\n\n"
            for product in products:
                text += f"🆔 {product[0]}. {product[1]}\n💰 السعر: {product[2]}$\n📦 المخزون: {product[3]}\n\n"
            # إضافة أزرار شراء لكل منتج
            keyboard = []
            for product in products:
                keyboard.append(
                    [InlineKeyboardButton(f"🛒 شراء {product[1]}", callback_data=f"buy_{product[0]}")]
                )
            keyboard.append([InlineKeyboardButton("🔙 الرجوع", callback_data="products")])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(
                f"⚠️ لا توجد منتجات متاحة من نوع {product_type_display} حالياً.\n",
                reply_markup=get_products_keyboard(),
            )

    elif data.startswith("buy_"):
        product_id = int(data.replace("buy_", ""))
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT name, price, stock FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        if product:
            name, price, stock = product
            if stock > 0:
                # خصم من المخزون
                c.execute("UPDATE products SET stock = stock - 1 WHERE id=?", (product_id,))
                # إضافة رصيد للمستخدم (محاكاة عملية شراء)
                add_balance(user.id, -price)  # ناقص لأن المستخدم دفع
                conn.commit()
                await query.edit_message_text(
                    f"✅ **تم الشراء بنجاح!**\n\n"
                    f"🛒 المنتج: {name}\n"
                    f"💰 السعر: {price}$\n"
                    f"📦 المخزون المتبقي: {stock - 1}\n\n"
                    f"شكراً لشرائك من متجرنا! 🎉",
                    parse_mode="Markdown",
                )
            else:
                await query.edit_message_text("⚠️ عذراً، هذا المنتج غير متوفر حالياً.")
        else:
            await query.edit_message_text("⚠️ المنتج غير موجود.")
        conn.close()

    elif data == "recharge":
        # شحن رصيد (محاكاة)
        keyboard = [
            [InlineKeyboardButton("💵 10$", callback_data="recharge_10")],
            [InlineKeyboardButton("💵 20$", callback_data="recharge_20")],
            [InlineKeyboardButton("💵 50$", callback_data="recharge_50")],
            [InlineKeyboardButton("🔙 الرجوع", callback_data="back_main")],
        ]
        await query.edit_message_text(
            "💰 **شحن الرصيد:**\n"
            "اختر المبلغ الذي تريد شحنه:\n\n"
            "🔹 سيتم تحويلك إلى بوابة الدفع بعد اختيار المبلغ.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("recharge_"):
        amount = int(data.replace("recharge_", ""))
        # محاكاة عملية شحن
        add_balance(user.id, amount)
        # التحقق من وجود مُحيل لإضافة المكافأة
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT referrer_id FROM users WHERE id=?", (user.id,))
        result = c.fetchone()
        if result and result[0]:
            referrer_id = result[0]
            add_referral_bonus(referrer_id, user.id, amount)
        conn.close()
        await query.edit_message_text(
            f"✅ **تم شحن رصيدك بنجاح!**\n\n"
            f"💰 المبلغ: {amount}$\n"
            f"💳 رصيدك الحالي: {get_user_balance(user.id)}$\n\n"
            f"شكراً لاستخدامك خدماتنا! 🎉",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(),
        )

    elif data == "support":
        support_id = "يوسف"  # يمكنك تغيير معرف الدعم هنا
        await query.edit_message_text(
            f"👤 **التواصل مع الدعم:**\n\n"
            f"للتواصل مع فريق الدعم، يمكنك مراسلة:\n"
            f"📱 المعرف: @{support_id}\n\n"
            f"سنسعد بخدمتك! 🤝",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(),
        )

    elif data == "referral":
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE id=?", (user.id,))
        if not c.fetchone():
            register_user(user)
        conn.close()
        referrals = get_referrals(user.id)
        referral_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user.id}"
        text = (
            f"👥 **نظام الإحالة:**\n\n"
            f"اربح 10% من قيمة شحن كل مستخدم جديد تسجله عن طريقك!\n\n"
            f"🔗 رابط الإحالة الخاص بك:\n"
            f"`{referral_link}`\n\n"
            f"📊 عدد المُحالين: {len(referrals)}\n"
        )
        if referrals:
            text += "\n📋 **قائمة المُحالين:**\n"
            for referred_id, bonus, created_at in referrals:
                text += f"• مستخدم {referred_id} - مكافأة: {bonus}$\n"
        await query.edit_message_text(text, parse_mode="Markdown")

    # ---------------------- Admin Handlers ----------------------
    elif data == "panel" and user.id == ADMIN_ID:
        await query.edit_message_text(
            "🔐 **لوحة التحكم - الأدمن**\n\n"
            "اختر الإجراء الذي تريد القيام به:",
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard(),
        )

    elif data.startswith("admin_") and user.id == ADMIN_ID:
        admin_action = data.replace("admin_", "")

        if admin_action == "stats":
            stats = get_stats()
            text = (
                "📊 **الإحصائيات:**\n\n"
                f"👥 زوار اليوم: {stats['today_visitors']}\n"
                f"👥 إجمالي الزوار: {stats['total_visitors']}\n"
                f"👤 إجمالي المستخدمين: {stats['total_users']}\n"
            )
            await query.edit_message_text(text, parse_mode="Markdown")

        elif admin_action == "exchange":
            rates = get_exchange_rates()
            text = "💱 **تعديل سعر الصرف:**\n\n"
            if rates:
                for currency, rate in rates.items():
                    text += f"• {currency}: {rate}$\n"
            text += "\n📝 لإضافة أو تعديل سعر الصرف، أرسل:\n`تعديل_سعر [العملة] [السعر]`\nمثال: تعديل_سعر USD 3.5"
            await query.edit_message_text(text, parse_mode="Markdown")

        elif admin_action == "products":
            products = get_all_products()
            if products:
                text = "📦 **جميع المنتجات:**\n\n"
                for product in products:
                    text += f"🆔 {product[0]}. {product[1]}\n💰 السعر: {product[2]}$\n📦 المخزون: {product[3]}\n🏷 النوع: {product[4]}\n\n"
                # إضافة أزرار لكل منتج للتعديل أو الحذف
                keyboard = []
                for product in products:
                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                f"✏️ تعديل {product[1]}", callback_data=f"edit_product_{product[0]}"
                            )
                        ]
                    )
                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                f"🗑 حذف {product[1]}", callback_data=f"delete_product_{product[0]}"
                            )
                        ]
                    )
                keyboard.append([InlineKeyboardButton("🔙 الرجوع", callback_data="panel")])
                await query.edit_message_text(
                    text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await query.edit_message_text("⚠️ لا توجد منتجات مسجلة حالياً.")

        elif admin_action == "add_product":
            context.user_data["admin_action"] = "add_product"
            await query.edit_message_text(
                "➕ **إضافة منتج جديد:**\n\n"
                "أرسل معلومات المنتج بالصيغة التالية:\n"
                "`الاسم | السعر | المخزون | النوع`\n\n"
                "مثال: `Apple ID جديد | 5.5 | 10 | Apple ID`\n"
                "📌 أنواع المنتجات المتاحة: Apple ID, Gmail, iCloud",
                parse_mode="Markdown",
            )
            return SELECTING_PRODUCT_NAME

        elif admin_action == "broadcast":
            context.user_data["admin_action"] = "broadcast"
            await query.edit_message_text(
                "📨 **إرسال رسالة للجميع:**\n\n"
                "أرسل الرسالة التي تريد نشرها لجميع المستخدمين.",
                parse_mode="Markdown",
            )
            return TYPING_REPLY

    # معالجة تعديل وحذف المنتجات
    elif data.startswith("edit_product_") and user.id == ADMIN_ID:
        product_id = int(data.replace("edit_product_", ""))
        context.user_data["edit_product_id"] = product_id
        context.user_data["admin_action"] = "edit_product"
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT name, price, stock FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        conn.close()
        if product:
            await query.edit_message_text(
                f"✏️ **تعديل المنتج:**\n\n"
                f"المنتج الحالي: {product[0]}\n"
                f"السعر: {product[1]}$\n"
                f"المخزون: {product[2]}\n\n"
                "أرسل المعلومات الجديدة بالصيغة:\n"
                "`الاسم | السعر | المخزون`\n"
                "مثال: `Apple ID جديد | 6.0 | 15`",
                parse_mode="Markdown",
            )
            return SELECTING_PRODUCT_NAME
        else:
            await query.edit_message_text("⚠️ المنتج غير موجود.")

    elif data.startswith("delete_product_") and user.id == ADMIN_ID:
        product_id = int(data.replace("delete_product_", ""))
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT name FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        if product:
            c.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            await query.edit_message_text(f"✅ تم حذف المنتج '{product[0]}' بنجاح!")
        else:
            await query.edit_message_text("⚠️ المنتج غير موجود.")
        conn.close()

    elif data == "recharge" and user.id == ADMIN_ID:
        # يمكن للأدمن إدارة عمليات الشحن
        pass

    else:
        await query.edit_message_text("⚠️ حدث خطأ، يرجى المحاولة مرة أخرى.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    user = update.effective_user
    text = update.message.text

    # التعامل مع أوامر الأدمن
    if user.id == ADMIN_ID and text.startswith("تعديل_سعر"):
        parts = text.split()
        if len(parts) == 3:
            currency = parts[1].upper()
            try:
                rate = float(parts[2])
                update_exchange_rate(currency, rate)
                await update.message.reply_text(f"✅ تم تحديث سعر {currency} إلى {rate}$")
            except ValueError:
                await update.message.reply_text("⚠️ السعر يجب أن يكون رقماً.")
        else:
            await update.message.reply_text("⚠️ الصيغة الصحيحة: `تعديل_سعر [العملة] [السعر]`")

    # إضافة منتج
    elif "admin_action" in context.user_data and context.user_data["admin_action"] == "add_product":
        try:
            parts = text.split("|")
            if len(parts) == 4:
                name = parts[0].strip()
                price = float(parts[1].strip())
                stock = int(parts[2].strip())
                type = parts[3].strip()
                add_product(name, price, stock, type)
                await update.message.reply_text("✅ تم إضافة المنتج بنجاح!")
            else:
                await update.message.reply_text("⚠️ الصيغة غير صحيحة. استخدم: `الاسم | السعر | المخزون | النوع`")
        except Exception as e:
            await update.message.reply_text(f"⚠️ حدث خطأ: {str(e)}")
        context.user_data.pop("admin_action", None)
        return ConversationHandler.END

    # تعديل منتج
    elif "admin_action" in context.user_data and context.user_data["admin_action"] == "edit_product":
        try:
            product_id = context.user_data.get("edit_product_id")
            parts = text.split("|")
            if len(parts) == 3:
                name = parts[0].strip()
                price = float(parts[1].strip())
                stock = int(parts[2].strip())
                update_product(product_id, name, price, stock)
                await update.message.reply_text("✅ تم تعديل المنتج بنجاح!")
            else:
                await update.message.reply_text("⚠️ الصيغة غير صحيحة. استخدم: `الاسم | السعر | المخزون`")
        except Exception as e:
            await update.message.reply_text(f"⚠️ حدث خطأ: {str(e)}")
        context.user_data.pop("admin_action", None)
        context.user_data.pop("edit_product_id", None)
        return ConversationHandler.END

    # بث رسالة للجميع
    elif "admin_action" in context.user_data and context.user_data["admin_action"] == "broadcast":
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users")
        users = c.fetchall()
        conn.close()
        sent_count = 0
        for user_id in users:
            try:
                await context.bot.send_message(
                    user_id[0],
                    f"📢 **رسالة من الإدارة:**\n\n{text}",
                    parse_mode="Markdown",
                )
                sent_count += 1
                await asyncio.sleep(0.05)  # لتجنب الحظر من تلغرام
            except Exception as e:
                logging.error(f"Failed to send to {user_id[0]}: {e}")
        await update.message.reply_text(f"✅ تم إرسال الرسالة إلى {sent_count} مستخدم.")
        context.user_data.pop("admin_action", None)
        return ConversationHandler.END

    # شحن رصيد للمستخدم (للأدمن)
    elif user.id == ADMIN_ID and text.startswith("شحن_رصيد"):
        parts = text.split()
        if len(parts) == 3:
            try:
                user_id = int(parts[1])
                amount = float(parts[2])
                add_balance(user_id, amount)
                await update.message.reply_text(f"✅ تم شحن {amount}$ للمستخدم {user_id}")
            except ValueError:
                await update.message.reply_text("⚠️ تأكد من صحة البيانات.")
        else:
            await update.message.reply_text("⚠️ الصيغة: `شحن_رصيد [أيدي المستخدم] [المبلغ]`")

    else:
        await update.message.reply_text(
            "⚠️ عذراً، لم أفهم طلبك. الرجاء استخدام الأزرار المتاحة.",
            reply_markup=get_main_keyboard(),
        )

    return ConversationHandler.END

async def set_commands(application: Application):
    commands = [
        BotCommand("start", "بدء استخدام البوت"),
        BotCommand("panel", "لوحة التحكم (للمسؤول فقط)"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    # تهيئة قاعدة البيانات
    init_db()
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    # إنشاء التطبيق مع تحديد حد الطلبات
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        # .rate_limiter(AIORateLimiter())  # معلق مؤقتاً
    )

    # معالج الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", start))

    # معالج الرسائل
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    # معالج الأزرار
    application.add_handler(CallbackQueryHandler(handle_callback))

    # تعيين أوامر البوت
    application.post_init = set_commands

    # بدء البوت
    print("🤖 البوت يعمل الآن...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
