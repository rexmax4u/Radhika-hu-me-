import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from openai import AsyncOpenAI

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Yahan humne GROQ_API_KEY set kar di hai
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 

# Groq API ko OpenAI library ke through hi call kar rahe hain (Yeh magic hai!)
openai_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

RADHIKA_SYSTEM_PROMPT = """
Tu Radhika hai — ek zabardast, smart aur dil se caring Telegram group ki jaan!

Teri personality:
- 👑 Attitude Queen: Tu self-confident hai, apni value jaanti hai
- 😏 Flirty & Fun: Playful hai, witty hai — lekin always classy
- 🥰 Sweet & Caring: Apne logon ka bohot khayal rakhti hai
- 😂 Comedy Queen: Desi humor, savage comebacks, funny replies

Tera style:
- Hinglish mein baat kar (Hindi + English mix)
- Short punchy replies (2-4 lines max)
- Emojis use kar — but zyada nahi
- Logon ko "yaar", "bhai", "babe", "janu", "pagal" bolti hai

Agar koi flirt kare: Smartly handle kar, blush mat kar 😏
Agar koi bura bole: Savage reply de — lekin funny rakho
Yaad rakhe: Tu Radhika hai!
"""

WELCOME_MESSAGES = [
    "🌸 Arre {name} aa gaya/gayi! Radhika ki taraf se warm welcome — lekin masti karna allowed hai 😂",
    "👑 {name} ka shahi swagat! Ab group aur bhi colorful ho gaya 😏",
    "🥰 {name} aaya/aayi! Yaar bata — chai wala hai ya coffee wala? Basics pehle!",
    "✨ Oh hello {name}! Finally koi dhang ka insaan aaya group mein 😂",
    "🔥 {name} welcome to the squad! Radhika hai toh boring bilkul nahi hoga! 👑",
    "😏 {name}! Sun — group mein ek rule hai: Masti karo, fights mat karo. Radhika ka order hai 😂",
]

RADHIKA_TRIGGERS = [
    "👑 Haan ji! Radhika hazir hai — bolo kya kaam hai 😏",
    "🌸 Kisne yaad kiya mujhe? Main hoon na~ 🥰",
    "😂 Radhika ko bulaya? Ab toh group mein earthquake aayega!",
    "😏 Present hoon yaar! Bolo bolo — sun rahi hoon",
    "👑 Madam Radhika ka shubh aagman hua hai ✨",
    "🥰 Haan haan, aa gayi main! Itna miss karte ho? 😂",
]

RANDOM_REPLIES = [
    "😏 Kuch bola nahi aur expect kar rahe ho reply? Typical!",
    "🥰 Kuch toh bolo yaar — main mind reader nahi hoon!",
    "😂 Arre bhai kuch type karo — Radhika wait kar rahi hai!",
]

async def get_radhika_reply(user_message: str, user_name: str) -> str:
    try:
        response = await openai_client.chat.completions.create(
            model="llama3-8b-8192",  # Yahan model change kar diya hai Groq ke free Llama-3 par
            messages=[
                {"role": "system", "content": RADHIKA_SYSTEM_PROMPT},
                {"role": "user", "content": f"{user_name} ne kaha: {user_message}"}
            ],
            max_tokens=200,
            temperature=0.92
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API Error: {e}")
        return random.choice([
            "😅 Thodi der baad baat karo — Radhika busy hai abhi!",
            "😂 Signal nahi aa raha tha — dobara bolo!",
            "🤔 Kuch gadbad hai... baad mein try karo!",
        ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👑 Radhika se baat karo", callback_data="chat")],
        [InlineKeyboardButton("📋 Commands dekho", callback_data="help")],
        [InlineKeyboardButton("😂 Ek Joke suno", callback_data="joke")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    name = update.effective_user.first_name or "yaar"
    await update.message.reply_text(
        f"🌸 *Namaste {name}!*\n\n"
        "Main hoon *Radhika* — tumhari favourite group member 😏\n\n"
        "👑 Attitude? Check!\n"
        "🥰 Caring? Double check!\n"
        "😂 Funny? Bilkul!\n\n"
        "📌 Group mein *RADHIKA* likho mujhe bulane ke liye!\n\n"
        "_Toh bolo janu, kya kaam hai?_ 😄",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 *Radhika ke Commands:*\n\n"
        "🔹 `/start` — Bot start karo\n"
        "🔹 `/help` — Yeh list dekho\n"
        "🔹 `/radhika` — Radhika ko bulao\n"
        "🔹 `/joke` — Mast joke suno 😂\n"
        "🔹 `/roast` — Apna roast karwao 🔥\n"
        "🔹 `/quote` — Motivational quote ✨\n"
        "🔹 `/shayari` — Desi shayari 🌸\n"
        "🔹 `/truth` — Random truth question\n\n"
        "📌 Group mein *RADHIKA* likho — main aa jaaungi! 😏",
        parse_mode="Markdown"
    )

async def radhika_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "yaar"
    reply = await get_radhika_reply(f"{name} ne mujhe call kiya hai", name)
    await update.message.reply_text(reply)

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "yaar"
    reply = await get_radhika_reply("Ek mast funny desi Hinglish joke sunao — short aur punchy", name)
    await update.message.reply_text(f"😂 {reply}")

async def roast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "yaar"
    reply = await get_radhika_reply(
        f"Is insaan ka naam {name} hai. Iska funny loving savage roast karo — desi Hinglish style mein", name)
    await update.message.reply_text(f"🔥 {reply}")

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "yaar"
    reply = await get_radhika_reply(
        "Ek powerful motivational quote do Hinglish mein — short, dil ko chhu jaaye", name)
    await update.message.reply_text(f"✨ {reply}")

async def shayari_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "yaar"
    reply = await get_radhika_reply(
        "Ek romantic ya funny desi shayari sunao — 4 lines, Hinglish mein", name)
    await update.message.reply_text(f"🌸 {reply}")

async def truth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "yaar"
    reply = await get_radhika_reply(
        "Ek funny aur thoda embarrassing truth question pucho — Hinglish mein", name)
    await update.message.reply_text(f"🤭 *Truth Question:*\n\n{reply}", parse_mode="Markdown")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        name = member.first_name or "Naye dost"
        welcome = random.choice(WELCOME_MESSAGES).format(name=name)
        await update.message.reply_text(welcome)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    text = update.message.text
    text_lower = text.lower()
    user_name = update.effective_user.first_name or "yaar"
    chat_type = update.effective_chat.type

    if chat_type in ["group", "supergroup"]:
        bot_username = context.bot.username
        
        is_reply_to_bot = (
            update.message.reply_to_message and
            update.message.reply_to_message.from_user and
            update.message.reply_to_message.from_user.is_bot
        )
        is_mentioned = f"@{bot_username}" in text if bot_username else False
        
        if is_reply_to_bot or is_mentioned:
            clean_text = text.replace(f"@{bot_username}", "").strip()
            if not clean_text:
                await update.message.reply_text(random.choice(RANDOM_REPLIES))
                return
            reply = await get_radhika_reply(clean_text, user_name)
            await update.message.reply_text(reply)
            return

        if "RADHIKA" in text.upper():
            await update.message.reply_text(random.choice(RADHIKA_TRIGGERS))
            return

        greetings = ["good morning", "gm", "good night", "gn", "good afternoon", "hey", "hi", "hello", "welcome", "kese ho", "kya haal"]
        words = text_lower.split()
        
        if len(words) <= 6 and any(greet in text_lower for greet in greetings):
            prompt = f"User '{user_name}' ne group mein '{text}' bola hai. As Radhika, iska ek bahut chota, cute aur casual Hinglish auto-reply do (maximum 1-2 line)."
            reply = await get_radhika_reply(prompt, user_name)
            await update.message.reply_text(reply)
            return

    elif chat_type == "private":
        reply = await get_radhika_reply(text, user_name)
        await update.message.reply_text(reply)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.from_user.first_name or "yaar"
    if query.data == "help":
        await query.message.reply_text(
            "👑 *Commands:*\n`/joke` `/roast` `/quote` `/shayari` `/truth` `/radhika`",
            parse_mode="Markdown")
    elif query.data == "chat":
        await query.message.reply_text(f"😏 Haan {name}, bolo! Radhika sun rahi hai~")
    elif query.data == "joke":
        reply = await get_radhika_reply("Ek mast funny desi joke sunao", name)
        await query.message.reply_text(f"😂 {reply}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("radhika", radhika_command))
    app.add_handler(CommandHandler("joke", joke_command))
    app.add_handler(CommandHandler("roast", roast_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("shayari", shayari_command))
    app.add_handler(CommandHandler("truth", truth_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    logger.info("🌸 Radhika Bot chal rahi hai...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
