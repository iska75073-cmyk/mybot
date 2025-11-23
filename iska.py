import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ТВОЙ ТОКЕН
TOKEN = "8389682572:AAGc0qAXKYWndTTguaphQ1Y2tbat5JITTp0"
bot = telebot.TeleBot(TOKEN)

user_data = {}

AUTHORIZED_FILE = "auth.txt"
KURS_FILE = "kurs.txt"

PASSWORD = "Sardor1994"   # ← твой пароль


# =====================================================
#        ХРАНЕНИЕ АВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ
# =====================================================

def load_authorized():
    if not os.path.exists(AUTHORIZED_FILE):
        return set()
    with open(AUTHORIZED_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_authorized(auth_set):
    with open(AUTHORIZED_FILE, "w") as f:
        for user in auth_set:
            f.write(str(user) + "\n")

authorized_users = load_authorized()


# =====================================================
#          ЗАГРУЗКА / СОХРАНЕНИЕ КУРСА
# =====================================================

def save_kurs(kurs):
    with open(KURS_FILE, "w") as f:
        f.write(str(kurs))

def load_kurs():
    if os.path.exists(KURS_FILE):
        try:
            with open(KURS_FILE, "r") as f:
                return float(f.read().strip())
        except:
            return None
    return None

loaded_kurs = load_kurs()
if loaded_kurs:
    user_data["global"] = {"kurs": loaded_kurs}
else:
    user_data["global"] = {}


# =====================================================
#          ВСПОМОГАТЕЛЬНЫЕ
# =====================================================

def send(chat_id, text, **kwargs):
    bot.send_message(chat_id, text, **kwargs)

def need_kurs(chat_id):
    return "kurs" not in user_data["global"]

def get_kurs():
    return user_data["global"]["kurs"]


# =====================================================
#        ЗАПРОС ПАРОЛЯ ПРИ ПЕРВОМ ВХОДЕ
# =====================================================

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    if str(chat_id) in authorized_users:
        return show_menu(message)

    send(chat_id, "🔐 Введите пароль для доступа:")
    bot.register_next_step_handler(message, check_password)


def check_password(message):
    chat_id = message.chat.id
    text = message.text

    if text == PASSWORD:
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass

        authorized_users.add(str(chat_id))
        save_authorized(authorized_users)

        send(chat_id, "✅ Пароль подтверждён!")
        return show_menu(message)

    else:
        send(chat_id, "❌ Неверный пароль!\nПопробуйте снова.")
        bot.register_next_step_handler(message, check_password)


# =====================================================
#                ГЛАВНОЕ МЕНЮ
# =====================================================

def show_menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = KeyboardButton("💛 Установить курс")
    btn2 = KeyboardButton("💱 UZS → USD")
    btn3 = KeyboardButton("💵 USD → UZS")
    btn4 = KeyboardButton("🛡 VIP Страховка (0 🟢)")
    btn5 = KeyboardButton("🟠 Страховка UZS")

    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4)
    markup.row(btn5)

    if need_kurs(message.chat.id):
        kurs_info = "❗ Курс не установлен"
    else:
        kurs_info = f"💛 Текущий курс: {get_kurs():.2f} UZS"

    send(
        message.chat.id,
        "✨ *PREMIUM GOLD BOT*\n"
        "────────────────────────\n"
        f"{kurs_info}\n\n"
        "Выберите раздел:",
        reply_markup=markup,
        parse_mode="Markdown"
    )


# =====================================================
#                УСТАНОВИТЬ КУРС
# =====================================================

@bot.message_handler(func=lambda m: m.text == "💛 Установить курс")
def ask_sum(message):
    if str(message.chat.id) not in authorized_users:
        return send(message.chat.id, "🔐 Сначала введите пароль через /start")

    send(
        message.chat.id,
        "💛 *Премиум установка курса*\n"
        "────────────────────────\n"
        "Введите сумму в 🇺🇿 UZS:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, get_sum)


def get_sum(message):
    try:
        uzs = float(message.text)
        user_data[message.chat.id] = {"uzs_paid": uzs}

        send(message.chat.id, "Теперь введите сумму, пришедшую в 💵 USD:")
        bot.register_next_step_handler(message, get_usd)

    except:
        send(message.chat.id, "❗ Введите корректное число!")
        bot.register_next_step_handler(message, get_sum)


def get_usd(message):
    try:
        usd = float(message.text)
        uzs = user_data[message.chat.id]["uzs_paid"]

        kurs = uzs / usd
        user_data["global"]["kurs"] = kurs

        save_kurs(kurs)

        send(
            message.chat.id,
            "✨ *Курс успешно установлен!*\n"
            "────────────────────────\n"
            f"💛 1 USD = *{kurs:.2f} UZS*",
            parse_mode="Markdown"
        )

    except:
        send(message.chat.id, "❗ Введите корректное число!")
        bot.register_next_step_handler(message, get_usd)


# =====================================================
#                 UZS → USD
# =====================================================

@bot.message_handler(func=lambda m: m.text == "💱 UZS → USD")
def uzs_to_usd(message):
    if need_kurs(message.chat.id):
        return send(message.chat.id, "❗ Сначала установите курс!")

    send(
        message.chat.id,
        "✨ *Конвертация UZS → USD*\n"
        "────────────────────────\n"
        "Введите сумму в 🇺🇿 UZS:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, convert_uzs_to_usd)


def convert_uzs_to_usd(message):
    try:
        uzs = float(message.text)
        kurs = get_kurs()

        usd = uzs / kurs

        send(
            message.chat.id,
            "✨ *Результат конвертации*\n"
            "────────────────────────\n"
            f"🇺🇿 {uzs} сум\n"
            f"💵 = *{usd:.2f} USD*\n"
            f"💛 Курс: {kurs:.2f}",
            parse_mode="Markdown"
        )
    except:
        send(message.chat.id, "❗ Введите корректное число!")


# =====================================================
#                 USD → UZS
# =====================================================

@bot.message_handler(func=lambda m: m.text == "💵 USD → UZS")
def usd_to_uzs(message):
    if need_kurs(message.chat.id):
        return send(message.chat.id, "❗ Сначала установите курс!")

    send(message.chat.id,
         "✨ *Конвертация USD → UZS*\n"
         "────────────────────────\n"
         "Введите сумму в 💵 USD:",
         parse_mode="Markdown")
    bot.register_next_step_handler(message, convert_usd_to_uzs)


def convert_usd_to_uzs(message):
    try:
        usd = float(message.text)
        kurs = get_kurs()

        uzs = usd * kurs

        send(
            message.chat.id,
            "✨ *Результат конвертации*\n"
            "────────────────────────\n"
            f"💵 {usd} USD\n"
            f"🇺🇿 = *{uzs:.2f} сум*\n"
            f"💛 Курс: {kurs:.2f}",
            parse_mode="Markdown"
        )
    except:
        send(message.chat.id, "❗ Введите корректное число!")


# =====================================================
#                 VIP СТРАХОВКА (USD)
# =====================================================

@bot.message_handler(func=lambda m: m.text == "🛡 VIP Страховка (0 🟢)")
def insurance_start(message):
    if need_kurs(message.chat.id):
        return send(message.chat.id, "❗ Сначала установите курс!")

    send(
        message.chat.id,
        "✨ *VIP Страховка (0)*\n"
        "────────────────────────\n"
        "Введите ставку (Stak) в USD:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, insurance_calc)


def insurance_calc(message):
    try:
        bet = float(message.text)
        kurs = get_kurs()

        stak = bet
        win1 = bet * kurs
        win2 = bet * kurs
        insurance = (bet * 3) / 36

        send(
            message.chat.id,
            "✨ *VIP Результат страховки*\n"
            "────────────────────────\n\n"
            f"🟥 *Stak:* \n{stak}$\n\n"
            f"🟧 *Win:* \n{bet}$ → {win1:.2f} сум\n\n"
            f"🟦 *Win:* \n{bet}$ → {win2:.2f} сум\n\n"
            "────────────────────────\n"
            f"🟢 *Страховка на 0:* \n"
            f"💛 *{insurance:.2f}$*",
            parse_mode="Markdown"
        )

    except:
        send(message.chat.id, "❗ Введите корректное число!")


# =====================================================
#                 СТРАХОВКА UZS
# =====================================================

@bot.message_handler(func=lambda m: m.text == "🟠 Страховка UZS")
def insurance_uzs_start(message):
    if need_kurs(message.chat.id):
        return send(message.chat.id, "❗ Сначала установите курс USD!")

    send(
        message.chat.id,
        "🟠 *Страховка UZS*\n"
        "────────────────────────\n"
        "Введите ставку (Stak) в 🇺🇿 UZS:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, insurance_uzs_calc)


def insurance_uzs_calc(message):
    try:
        bet_uzs = float(message.text)

        insurance = (bet_uzs * 3) / 36

        send(
            message.chat.id,
            "🟠 *Результат страховки UZS*\n"
            "────────────────────────\n\n"
            f"🟥 *Stak:* \n{bet_uzs:,.2f} сум\n\n"
            f"🟧 *Win:* \n{bet_uzs:,.2f} сум\n\n"
            f"🟦 *Win:* \n{bet_uzs:,.2f} сум\n\n"
            "────────────────────────\n"
            f"🟢 *Страховка на 0:* \n"
            f"💛 *{insurance:,.2f} сум*",
            parse_mode="Markdown"
        )

    except:
        send(message.chat.id, "❗ Введите корректное число!")


# =====================================================
bot.infinity_polling()