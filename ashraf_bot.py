import requests
import time
import json
import re
import os
import scheduler
import google_calendar
import speech_recognition as sr
from pydub import AudioSegment
from datetime import datetime

BOT_TOKEN = '8005958189:AAHjHOQnwQjU3A0k62-ue4BMkpUdxs03VP0'
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
MEMORY_FILE = 'memory.json'
LAST_UPDATE_ID = None

def load_memory():
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def log_entry(category, content):
    memory = load_memory()
    entry = {
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    memory[category].append(entry)
    save_memory(memory)

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, data=payload)

def transcribe_voice(file_path):
    sound = AudioSegment.from_ogg(file_path)
    wav_path = file_path.replace('.ogg', '.wav')
    sound.export(wav_path, format="wav")

    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language="en-US")
        return text, "en"
    except sr.UnknownValueError:
        try:
            text = r.recognize_google(audio, language="ar-EG")
            return text, "ar"
        except:
            return None, None

def download_file(file_id, file_path):
    file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info['result']['file_path']}"
    r = requests.get(file_url)
    with open(file_path, 'wb') as f:
        f.write(r.content)

def handle_message(message, chat_id, lang="en"):
    lower = message.lower()

    # Language templates
    reply = lambda en, ar: en if lang == "en" else ar

    if "prayed" in lower or "صليت" in lower:
        log_entry("prayers", message)
        send_message(chat_id, reply("🕌 Noted! I’ve saved that you prayed.", "🕌 سجلت إنك صليت."))
    elif "gym" in lower or "جيم" in lower:
        log_entry("gym", message)
        send_message(chat_id, reply("🏋️ Logged! You're staying consistent!", "🏋️ تمام! سجلت التمرين بتاعك."))
    elif "task" in lower or "remind me" in lower or "مهمة" in lower or "فكرني" in lower:
        log_entry("tasks", message)
        send_message(chat_id, reply("📌 Task saved. I’ll remind you soon.", "📌 تمام، سجلت المهمة وهفكرك بيها."))
    elif "note" in lower or "ملاحظة" in lower:
        log_entry("notes", message)
        send_message(chat_id, reply("📝 Note stored!", "📝 حفظت الملاحظة."))
    elif "meeting" in lower or "اجتماع" in lower:
        log_entry("meetings", message)
        send_message(chat_id, reply("📆 Meeting saved!", "📆 سجلت الاجتماع."))
    elif "presentation" in lower or "عرض" in lower:
        log_entry("presentations", message)
        send_message(chat_id, reply("📊 Presentation logged.", "📊 سجلت العرض التقديمي."))
    elif "orientation" in lower or "توجيه" in lower:
        log_entry("orientations", message)
        send_message(chat_id, reply("🧭 Orientation added.", "🧭 سجلت جلسة التوجيه."))
    elif "event" in lower or "فعالية" in lower:
        log_entry("events", message)
        send_message(chat_id, reply("🎯 Event saved!", "🎯 سجلت الحدث."))
    elif "team" in lower or "الفريق" in lower:
        log_entry("team", message)
        send_message(chat_id, reply("👥 Team update saved.", "👥 سجلت ملاحظة عن الفريق."))
    elif "mood:" in lower or "i feel" in lower or "حاسس" in lower:
        log_entry("mood", message)
        send_message(chat_id, reply("🧠 Mood logged. I’m always here to listen.", "🧠 سجلت حالتك المزاجية. أنا دايمًا معاك."))
    elif "i ate" in lower or "food:" in lower or "أكلت" in lower:
        log_entry("food", message)
        send_message(chat_id, reply("🍽️ Got it. Your meal is saved.", "🍽️ تمام، سجلت وجبتك."))
    elif "recipe:" in lower or "save recipe" in lower or "وصفة" in lower:
        log_entry("recipes", message)
        send_message(chat_id, reply("📖 Recipe saved! I’ll keep it handy.", "📖 سجلت الوصفة وهفتكرها دايمًا."))
    elif "show mood" in lower or "اعرض الحالة" in lower:
        moods = load_memory()["mood"]
        response = "\n".join([f"- {m['content']} at {m['timestamp']}" for m in moods[-5:]]) or reply("No mood logs yet.", "لسه مفيش حالات مزاجية مسجلة.")
        send_message(chat_id, response)
    elif "suggest recipe" in lower or "اقتراح وجبة" in lower:
        recipes = load_memory()["recipes"]
        if recipes:
            suggestion = recipes[-1]["content"]
            send_message(chat_id, reply(f"🍲 How about this one: {suggestion}", f"🍲 جرب دي: {suggestion}"))
        else:
            send_message(chat_id, reply("Hmm… I don’t have any recipes saved yet!", "لسه معنديش وصفات محفوظة."))
    elif "schedule" in lower or "add event" in lower or "ميعاد" in lower or "موعد" in lower:
        try:
            match = re.search(r"(?:schedule|add event|ميعاد|موعد)[:\-]?\s*(.+?)\s*on\s*(\d{4}-\d{2}-\d{2})\s*at\s*(\d{1,2}:\d{2})", lower)
            if match:
                title = match.group(1).strip().capitalize()
                date = match.group(2)
                time_ = match.group(3)
                start_str = f"{date} {time_}"
                link = google_calendar.create_event(title, start_str)
                send_message(chat_id, reply(
                    f"📅 Event created: {title}\n🕒 {start_str}\n🔗 {link}",
                    f"📅 سجلت الحدث: {title}\n🕒 {start_str}\n🔗 {link}"
                ))
            else:
                send_message(chat_id, reply(
                    "⚠️ Couldn't understand the event format. Try:\nSchedule: Meeting with Omar on 2025-04-06 at 14:30",
                    "⚠️ مش قادر أفهم صيغة الميعاد. جرب: ميعاد: اجتماع مع عمر on 2025-04-06 at 14:30"
                ))
        except Exception as e:
            send_message(chat_id, reply(
                f"❌ Error creating event: {e}",
                f"❌ حصل خطأ وأنا بسجل الحدث: {e}"
            ))
    else:
        send_message(chat_id, reply("✅ Got it! I saved that info.", "✅ تمام! سجلت المعلومة."))

def get_updates():
    global LAST_UPDATE_ID
    url = f"{BASE_URL}/getUpdates"
    if LAST_UPDATE_ID:
        url += f"?offset={LAST_UPDATE_ID + 1}"
    res = requests.get(url)
    return res.json()['result']

def run():
    global LAST_UPDATE_ID
    scheduler.start()  # start background reminders

    while True:
        updates = get_updates()
        for update in updates:
            LAST_UPDATE_ID = update['update_id']
            message_data = update['message']
            chat_id = message_data['chat']['id']

            if 'voice' in message_data:
                file_id = message_data['voice']['file_id']
                ogg_path = f"voice_{chat_id}.ogg"
                download_file(file_id, ogg_path)
                try:
                    text, lang = transcribe_voice(ogg_path)
                    if text:
                        echo = "🗣 You said: " if lang == "en" else "🗣 إنت قلت: "
                        send_message(chat_id, echo + text)
                        handle_message(text, chat_id, lang)
                    else:
                        send_message(chat_id, "❌ معرفتش أفهم الصوت.")
                except Exception as e:
                    send_message(chat_id, f"❌ Error processing voice: {e}")
                os.remove(ogg_path)
                os.remove(ogg_path.replace('.ogg', '.wav'))

            elif 'text' in message_data:
                text = message_data['text']
                handle_message(text, chat_id, "en")

        time.sleep(1)

if __name__ == "__main__":
    run()
