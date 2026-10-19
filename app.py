"""TOM Assistant — a small conversational Telegram bot (webhook mode)."""
import os
import re
import random
from datetime import datetime

import requests
from flask import Flask, request, jsonify

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

app = Flask(__name__)


# ---------------------------------------------------------------- brain ---

def pick_response(text: str) -> str:
    t = text.lower().strip()

    if t in ("/start", "start"):
        return (
            "Hey! I'm TOM Assistant. 👋\n"
            "Chat with me — ask how I am, ask for a joke, or just say hi.\n"
            "Type /help to see what I can do."
        )
    if t == "/help":
        return (
            "Here's what I can do:\n"
            "• Say hello / hi / namaste\n"
            "• Ask 'how are you?'\n"
            "• Ask 'what's your name?'\n"
            "• Ask for a joke\n"
            "• Ask for the time or date\n"
            "• Just chat — I'll keep up!"
        )

    if re.search(r"\b(hello|hi+|hey+|namaste|salaam|yo|hii+)\b", t):
        return random.choice([
            "Hey there! How's it going?",
            "Hello! Good to see you. What's up?",
            "Namaste! Kaise ho?",
            "Hey hey! What are we chatting about today?",
        ])

    if re.search(r"how are you|how r u|kais[ae] ho|aur batao", t):
        return random.choice([
            "I'm doing great, thanks for asking! How about you?",
            "All good here — running smooth. And you?",
            "Badhiya! Tum sunao, kya chal raha hai?",
        ])

    if re.search(r"your name|tumhara naam|who are you|tum kaun", t):
        return "I'm TOM Assistant — a friendly little bot. And you are?"

    if re.search(r"\bmy name is\b", t):
        name = re.sub(r".*\bmy name is\b", "", t).strip().split()[0:1]
        name = name[0].capitalize() if name else "friend"
        return f"Nice to meet you, {name}! I'll remember that... well, for this chat at least. 😄"

    if re.search(r"\bjoke\b|\bhasi\b|funny|hasa", t):
        return random.choice([
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "I told my computer I needed a break… now it won't stop sending me KitKat ads. 🍫",
            "Why did the phone go to school? To improve its cell-f! 📱",
            "Ek tha raja, ek thi rani… dono ne mujhe joke sunane ko kaha, aur main phas gaya! 😂",
            "Why don't programmers like nature? Too many bugs. 🐞",
        ])

    if re.search(r"\btime\b|samay|kitne baje", t):
        return "It's " + datetime.now().strftime("%I:%M %p") + " right now. ⏰"

    if re.search(r"\bdate\b|tarikh|aaj ka din", t):
        return "Today is " + datetime.now().strftime("%A, %d %B %Y") + ". 📅"

    if re.search(r"\b(thank|shukriya|dhanyavad)\b", t):
        return random.choice([
            "You're welcome! 😊",
            "Anytime! That's what I'm here for.",
            "Koi baat nahi! 👍",
        ])

    if re.search(r"\b(bye|alvida|good night|goodnight|see you)\b", t):
        return random.choice([
            "Bye! Come chat again soon. 👋",
            "Alvida! Phir milenge. 😊",
            "Good night! Sweet dreams. 🌙",
        ])

    if re.search(r"\b(help|madad)\b", t):
        return "Type /help to see everything I can do!"

    if re.search(r"\bi love you\b", t):
        return "Aww, that's sweet! I like you too — as a friend. 😊"

    # fallback: keep the conversation going
    return random.choice([
        f"Interesting — tell me more about \"{text[:60]}\".",
        "Hmm, I see. What else is on your mind?",
        "Got it! Anything else you want to chat about?",
        "I'm still learning, but I'm listening. Go on…",
    ])


def send_message(chat_id: int, text: str) -> None:
    if not API:
        app.logger.error("BOT_TOKEN is not set")
        return
    try:
        requests.post(
            f"{API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except Exception as exc:  # noqa: BLE001 — keep the webhook alive
        app.logger.error("sendMessage failed: %s", exc)


# --------------------------------------------------------------- routes ---

@app.get("/")
def index():
    return jsonify(status="ok", service="tom-assistant-bot")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/webhook")
def webhook():
    update = request.get_json(force=True, silent=True) or {}
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "")
    if chat_id and text:
        send_message(chat_id, pick_response(text))
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
