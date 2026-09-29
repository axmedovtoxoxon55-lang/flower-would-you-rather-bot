# ============================================
# 🌸 FLOWER WOULD YOU RATHER BOT
# ============================================

!pip install -q pyTelegramBotAPI

import telebot
from telebot import types
import sqlite3
import random

# ============================================
# 🔑 TOKEN
# ============================================

TOKEN = ""

bot = telebot.TeleBot(TOKEN)

# ============================================
# 🌷 GULLAR
# ============================================

flowers = {
    "rose": "🌹 Atirgul",
    "tulip": "🌷 Lola",
    "sunflower": "🌻 Kungaboqar",
    "lily": "🌸 Liliya",
    "chrysanthemum": "🌼 Xrizantema",
    "orchid": "🌺 Orxideya",
    "peony": "🌸 Pion"
}

# ============================================
# 💾 DATABASE
# ============================================

db = sqlite3.connect(
    "flower_results.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
    user_id INTEGER,
    flower TEXT
)
""")

db.commit()

# ============================================
# 👤 O'YINLAR
# ============================================

games = {}

# ============================================
# 🏠 BOSH MENYU
# ============================================

def main_menu():

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "🌸 O'yinni boshlash",
            callback_data="start_game"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "📊 Mening natijam",
            callback_data="my_result"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🌍 Umumiy statistika",
            callback_data="global_result"
        )
    )

    return markup


# ============================================
# 🚀 /START
# ============================================

@bot.message_handler(commands=["start"])
def start(message):

    text = """
🌸 <b>GUL TANLASH O'YINIGA XUSH KELIBSIZ!</b>

Bu o'yin <b>Would You Rather</b> uslubida ishlaydi.

Sizga ikkita gul ko'rsatiladi.
Ulardan o'zingizga ko'proq yoqadigan bittasini tanlaysiz. ❤️

Tanlovlaringiz asosida oxirida:
🌷 Eng ko'p yoqtirgan gullaringiz
❌ Umuman tanlamagan gullaringiz

ko'rsatiladi.

🌸 Jami 10 tagacha savol bo'ladi.

Tayyor bo'lsangiz, boshlang 👇
"""

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ============================================
# 🎮 O'YINNI BOSHLASH
# ============================================

@bot.callback_query_handler(
    func=lambda call: call.data == "start_game"
)
def start_game(call):

    user_id = call.from_user.id

    games[user_id] = {
        "question": 0,
        "total_questions": 10,

        "scores": {
            flower: 0
            for flower in flowers
        },

        "current_pair": None,

        # Tanlangan gullarni saqlaymiz
        "selected_flowers": []
    }

    bot.answer_callback_query(call.id)

    send_question(
        call.message.chat.id,
        user_id
    )


# ============================================
# ❓ SAVOL YUBORISH
# ============================================

def send_question(chat_id, user_id):

    game = games[user_id]

    question_number = game["question"] + 1
    total = game["total_questions"]

    flower_ids = list(flowers.keys())

    # 2 ta har xil gul
    flower1, flower2 = random.sample(
        flower_ids,
        2
    )

    game["current_pair"] = (
        flower1,
        flower2
    )

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

    markup.add(
        types.InlineKeyboardButton(
            flowers[flower1],
            callback_data=f"choose_{flower1}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            flowers[flower2],
            callback_data=f"choose_{flower2}"
        )
    )

    text = f"""
🌸 <b>Qaysi gulni tanlaysiz?</b>

<b>{question_number}/{total}</b>

❤️ O'zingizga ko'proq yoqqanini tanlang:
"""

    bot.send_message(
        chat_id,
        text,
        parse_mode="HTML",
        reply_markup=markup
    )


# ============================================
# 🌷 GUL TANLANGANDA
# ============================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("choose_")
)
def choose_flower(call):

    user_id = call.from_user.id

    if user_id not in games:

        bot.answer_callback_query(
            call.id,
            "Avval o'yinni boshlang!"
        )

        return

    game = games[user_id]

    selected_flower = call.data.replace(
        "choose_",
        ""
    )

    # ========================================
    # TANLOVNI TEKSHIRISH
    # ========================================

    # Faqat joriy savoldagi gulni qabul qilamiz
    if selected_flower not in game["current_pair"]:

        bot.answer_callback_query(
            call.id,
            "Bu gul hozirgi savolga tegishli emas."
        )

        return

    # ========================================
    # BALL QO'SHISH
    # ========================================

    game["scores"][selected_flower] += 1

    # Tanlangan gullar ro'yxatiga qo'shamiz
    if selected_flower not in game["selected_flowers"]:

        game["selected_flowers"].append(
            selected_flower
        )

    # ========================================
    # DATABASE
    # ========================================

    cursor.execute(
        """
        INSERT INTO votes (user_id, flower)
        VALUES (?, ?)
        """,
        (
            user_id,
            selected_flower
        )
    )

    db.commit()

    bot.answer_callback_query(
        call.id,
        f"Tanladingiz: {flowers[selected_flower]}"
    )

    # ========================================
    # SAVOL RAQAMINI OSHIRISH
    # ========================================

    game["question"] += 1

    # ========================================
    # KEYINGI SAVOL
    # ========================================

    if game["question"] < game["total_questions"]:

        send_question(
            call.message.chat.id,
            user_id
        )

    else:

        show_final_result(
            call.message.chat.id,
            user_id
        )


# ============================================
# 🏆 YAKUNIY NATIJA
# ============================================

def show_final_result(chat_id, user_id):

    game = games[user_id]

    scores = game["scores"]

    # ========================================
    # ENG KO'P TANLANGAN GULLAR
    # ========================================

    max_score = max(
        scores.values()
    )

    winners = [
        flower
        for flower, score in scores.items()
        if score == max_score and score > 0
    ]

    # ========================================
    # TANLANMAGAN GULLAR
    # ========================================

    not_selected = [
        flower
        for flower, score in scores.items()
        if score == 0
    ]

    # ========================================
    # NATIJA MATNI
    # ========================================

    text = """
🏆 <b>O'YIN TUGADI!</b>

🌸 <b>SIZNING NATIJANGIZ:</b>

"""

    # Faqat tanlangan gullarni chiqaramiz
    selected_results = [
        (flower, score)
        for flower, score in scores.items()
        if score > 0
    ]

    selected_results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    for flower, score in selected_results:

        text += (
            f"{flowers[flower]} — "
            f"<b>{score}</b> ta tanlov\n"
        )

    # ========================================
    # SEVIMLI GUL
    # ========================================

    text += "\n"

    if len(winners) == 1:

        winner = winners[0]

        text += (
            f"❤️ <b>Siz eng ko'p "
            f"{flowers[winner]}ni tanladingiz!</b>\n"
        )

    else:

        winner_names = [
            flowers[w]
            for w in winners
        ]

        text += (
            "❤️ <b>Siz eng ko'p tanlagan gullar:</b>\n"
            + "\n".join(winner_names)
            + "\n"
        )

    # ========================================
    # ❌ YOQTIRILMAGAN / TANLANMAGAN GULLAR
    # ========================================

    if not_selected:

        text += (
            "\n❌ <b>Siz tanlamagan gullar:</b>\n"
        )

        for flower in not_selected:

            text += (
                f"{flowers[flower]}\n"
            )

    else:

        text += (
            "\n🌟 <b>Siz barcha gullardan "
            "kamida bittasini tanladingiz!</b>\n"
        )

    # ========================================
    # TUGMALAR
    # ========================================

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔄 Yana o'ynash",
            callback_data="start_game"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🌍 Umumiy statistika",
            callback_data="global_result"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🏠 Bosh menyu",
            callback_data="home"
        )
    )

    bot.send_message(
        chat_id,
        text,
        parse_mode="HTML",
        reply_markup=markup
    )


# ============================================
# 📊 MENING NATIJAM
# ============================================

@bot.callback_query_handler(
    func=lambda call: call.data == "my_result"
)
def my_result(call):

    user_id = call.from_user.id

    cursor.execute(
        """
        SELECT flower, COUNT(*)
        FROM votes
        WHERE user_id = ?
        GROUP BY flower
        ORDER BY COUNT(*) DESC
        """,
        (user_id,)
    )

    results = cursor.fetchall()

    bot.answer_callback_query(
        call.id
    )

    if not results:

        bot.send_message(
            call.message.chat.id,

            "📊 Hali hech qanday natijangiz yo'q.\n\n"
            "🌸 O'yinni boshlang!",

            reply_markup=main_menu()
        )

        return

    text = (
        "📊 <b>SIZNING NATIJANGIZ</b>\n\n"
    )

    for flower, count in results:

        text += (
            f"{flowers[flower]} — "
            f"<b>{count}</b> ta\n"
        )

    favorite = results[0][0]

    text += (
        f"\n❤️ Siz hozirgacha eng ko'p "
        f"<b>{flowers[favorite]}</b>ni "
        f"tanlagansiz."
    )

    bot.send_message(
        call.message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ============================================
# 🌍 UMUMIY STATISTIKA
# ============================================

@bot.callback_query_handler(
    func=lambda call: call.data == "global_result"
)
def global_result(call):

    cursor.execute(
        """
        SELECT flower, COUNT(*)
        FROM votes
        GROUP BY flower
        ORDER BY COUNT(*) DESC
        """
    )

    results = cursor.fetchall()

    bot.answer_callback_query(
        call.id
    )

    if not results:

        bot.send_message(
            call.message.chat.id,
            "🌍 Hali umumiy natijalar mavjud emas.",
            reply_markup=main_menu()
        )

        return

    total_votes = sum(
        count
        for flower, count in results
    )

    text = (
        "🌍 <b>UMUMIY STATISTIKA</b>\n\n"
    )

    for flower, count in results:

        percentage = (
            count / total_votes * 100
        )

        text += (
            f"{flowers[flower]} — "
            f"<b>{count}</b> ta "
            f"({percentage:.1f}%)\n"
        )

    text += (
        f"\n👥 Jami tanlovlar: "
        f"<b>{total_votes}</b>"
    )

    bot.send_message(
        call.message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ============================================
# 🏠 BOSH MENYU
# ============================================

@bot.callback_query_handler(
    func=lambda call: call.data == "home"
)
def home(call):

    bot.answer_callback_query(
        call.id
    )

    bot.send_message(
        call.message.chat.id,

        "🌸 <b>Bosh menyu</b>\n\n"
        "Nima qilmoqchisiz?",

        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ============================================
# 🤖 BOTNI ISHGA TUSHIRISH
# ============================================

print("===================================")
print("🌸 FLOWER BOT ISHLAYAPTI!")
print("===================================")
print("Telegram'da botga /start yuboring.")

bot.infinity_polling()
