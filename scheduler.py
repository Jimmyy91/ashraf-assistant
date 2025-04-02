import schedule
import time
import threading
from datetime import datetime
import requests
import json

# BOT SETTINGS
BOT_TOKEN = '8005958189:AAHjHOQnwQjU3A0k62-ue4BMkpUdxs03VP0'
CHAT_ID = '6524089840'  # <-- replace with your Telegram user ID
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
MEMORY_FILE = 'memory.json'

def load_memory():
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f)

def send_message(text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

def morning_message():
    send_message("☀️ Good morning, Amr! Let’s conquer the day 💼\n\nWhat’s your top priority today?")

def night_checkin():
    send_message("🌙 How was your day, Amr?\n- Did you go to the gym?\n- How was your mood?\n- Want to log anything?")

def friday_summary():
    data = load_memory()
    tasks = len(data["tasks"])
    prayers = len(data["prayers"])
    mood_logs = len(data["mood"])
    gym_logs = len(data["gym"])
    food_logs = len(data["food"])

    summary = f"""📊 *Your Weekly Summary*
Tasks saved: {tasks}
Prayers logged: {prayers}
Mood entries: {mood_logs}
Gym sessions: {gym_logs}
Meals tracked: {food_logs}

🔥 Let’s keep it up next week! 💪
"""
    send_message(summary)

# Schedule jobs
schedule.every().day.at("08:00").do(morning_message)
schedule.every().day.at("21:00").do(night_checkin)
schedule.every().friday.at("08:00").do(friday_summary)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start():
    thread = threading.Thread(target=run_scheduler)
    thread.start()
