import telebot
import sqlite3
from flask import Flask, request
from datetime import datetime
import os

# إعدادات البوت
TOKEN = "ضع_هنا_توكن_بوت_فاذر"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, content TEXT)')
    conn.commit()
    return conn

db_conn = init_db()

# --- استقبال البيانات من موقعك ---
@app.route('/webhook', methods=['POST'])
def receive_from_site():
    data = request.get_data(as_text=True) # افترضنا أن الموقع يرسل نصاً بسيطاً
    if data:
        # حفظ في القاعدة
        cursor = db_conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO reports (date, content) VALUES (?, ?)", (now, data))
        db_conn.commit()
        
        # إرسال إشعار فوري لك
        bot.send_message("ID_حسابك_هنا", f"🔔 تبليغ جديد من الموقع:\n{data}")
        return "OK", 200
    return "No Data", 400

# --- أوامر التقرير في تيليجرام ---
@bot.message_handler(commands=['report'])
def send_report(message):
    cursor = db_conn.cursor()
    cursor.execute("SELECT date, content FROM reports ORDER BY id DESC")
    rows = cursor.fetchall()
    
    if not rows:
        bot.reply_to(message, "📭 لا توجد تبليغات.")
        return

    report_text = "📊 **جميع التبليغات:**\n\n"
    for row in rows:
        report_text += f"📅 {row[0]}\n📝 {row[1]}\n---\n"
    
    bot.reply_to(message, report_text)

# تشغيل البوت مع Flask
if __name__ == "__main__":
    # ملاحظة: في الاستضافات الحقيقية نستخدم برامج مثل Gunicorn
    from threading import Thread
    Thread(target=lambda: bot.polling(non_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
