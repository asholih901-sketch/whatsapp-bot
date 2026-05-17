import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from datetime import datetime
from groq import Groq

app = Flask(__name__)

TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
VALIDATE_REQUESTS = bool(TWILIO_AUTH_TOKEN)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def build_reply(incoming_msg: str) -> str:
    msg = incoming_msg.strip().lower()

    if any(w in msg for w in ["halo", "hi", "hello", "hai", "hey"]):
        return (
            "Halo! Saya adalah WhatsApp Bot otomatis Buatan *MUHAMMAD AHMAD SHOLIH*.\n\n"
            "Ketik *bantuan* untuk melihat daftar perintah yang tersedia."
        )

    if any(w in msg for w in ["bantuan", "help", "menu"]):
        return (
            "*Daftar Perintah:*\n\n"
            "- *halo* - Sapa bot\n"
            "- *info* - Informasi tentang bot\n"
            "- *pembuat* - Info tentang pembuat bot\n"
            "- *jam* - Lihat waktu sekarang\n"
            "- *bantuan* - Tampilkan menu ini\n\n"
            "Kirim pesan apapun dan saya akan membalasnya menggunakan AI!"
        )

    if "info" in msg:
        return (
            "*Info Bot*\n\n"
            "Saya adalah WhatsApp Bot yang dibangun dengan:\n"
            "- Python Flask\n"
            "- Twilio WhatsApp API\n"
            "- Groq AI (Llama 3.1)\n\n"
            "Bot ini membalas pesan secara otomatis."
        )

    if any(w in msg for w in ["pembuat", "creator", "tentang"]):
        return (
            "*Tentang Pembuat Bot* 👨‍💻\n\n"
            "Nama: M Ahmad Sholih\n"
            "Instagram: @mads_if\n"
            "Asal: Indonesia\n"
            "Hobi: Belajar programming\n\n"
            "Bot ini dibuat sebagai proyek belajar!"
        )

    if any(w in msg for w in ["jam", "waktu", "time"]):
        now = datetime.now().strftime("%H:%M:%S")
        date = datetime.now().strftime("%d %B %Y")
        return f"Sekarang pukul *{now}*\nTanggal: *{date}*"

    try:
        instruksi = "Kamu adalah asisten WhatsApp milik M Ahmad Sholih. Ahmad adalah pemilik bot ini, seorang pemuda Indonesia yang sedang belajar programming jika anda penasaran dengan dirinya ikuti ig nya (mads_if). Jika ditanya tentang Ahmad atau pemilik bot, jawab sesuai info ini. Jawab semua pertanyaan pakai bahasa Indonesia yang santai."
        respons = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": instruksi},
                {"role": "user", "content": incoming_msg}
            ]
        )
        return respons.choices[0].message.content
    except Exception as e:
        return "Waduh, AI lagi bermasalah nih. Coba lagi ya!"

@app.route("/webhook", methods=["POST"])
def webhook():
    if VALIDATE_REQUESTS:
        validator = RequestValidator(TWILIO_AUTH_TOKEN)
        signature = request.headers.get("X-Twilio-Signature", "")
        if not validator.validate(request.url, request.form.to_dict(), signature):
            return Response("Forbidden", status=403)

    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "unknown")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Pesan dari {sender}: {incoming_msg}")

    resp = MessagingResponse()
    resp.message(build_reply(incoming_msg))

    return Response(str(resp), mimetype="application/xml")

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "whatsapp-bot"}, 200

@app.route("/", methods=["GET"])
def index():
    return {
        "service": "WhatsApp Bot",
        "status": "running",
        "webhook_endpoint": "POST /webhook"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)