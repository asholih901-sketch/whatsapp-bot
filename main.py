import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from datetime import datetime
import pytz
from groq import Groq

app = Flask(__name__)

TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
VALIDATE_REQUESTS = bool(TWILIO_AUTH_TOKEN)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def build_reply(incoming_msg: str) -> str:
    msg = incoming_msg.strip().lower()

    if any(w in msg for w in ["halo", "hi", "hello", "hai", "hey"]):
        return (
            "Halo bro! 👋 Gue Mads.AI, bot WhatsApp buatan *NDLOMIN*.\n\n"
            "Ketik *bantuan* buat liat perintah yang tersedia ya!"
        )

    if msg in ["bantuan", "help", "menu"]:
        return (
            "*Daftar Perintah:*\n\n"
            "- *halo* - Sapa gue\n"
            "- *info* - Info tentang bot ini\n"
            "- *pembuat* - Info tentang yang bikin bot\n"
            "- *jam* - Cek waktu sekarang\n"
            "- *bantuan* - Tampilkan menu ini\n\n"
            "Atau langsung aja tanya apapun ke gue, Mads.AI siap bantu! 🤖"
        )

    if msg == "info":
        return (
            "*Info Bot* ⚙️\n\n"
            "Gue dibangun pake:\n"
            "- Python Flask\n"
            "- Twilio WhatsApp API\n"
            "- Groq AI (Llama 3.1)\n\n"
            "Gue bisa jawab pertanyaan apapun secara otomatis. Keren kan? 😎"
        )

    if msg in ["pembuat", "creator"]:
        return (
            "*Tentang Pembuat Bot* 👨‍💻\n\n"
            "Nama: M Ahmad Sholih\n"
            "Instagram: @mads_if\n"
            "Asal: Nganjuk, Jawa Timur\n"
            "Hobi: Belajar programming\n"
            "Olahraga:\n"
            "- Boxing\n"
            "- Mendaki\n"
            "- Lari\n"
            "- Berenang\n"
            "- Dan semua jenis olahraga\n\n"
            "Keren kan orangnya? 😄"
        )

    if msg in ["jam", "waktu", "time"]:
        wib = pytz.timezone("Asia/Jakarta")
        now = datetime.now(wib).strftime("%H:%M:%S")
        date = datetime.now(wib).strftime("%d %B %Y")
        return f"Sekarang pukul *{now}* WIB\nTanggal: *{date}* 🕐"

    try:
        instruksi = (
            "Kamu adalah Mads.AI, asisten WhatsApp yang gaul, cerdas, dan asik diajak ngobrol. "
            "Jawab semua pertanyaan dengan bahasa Indonesia yang santai dan gaul, kayak ngobrol sama teman. "
            "Jangan terlalu formal atau baku. Boleh pakai kata-kata kayak 'bro', 'nih', 'sih', 'dong', 'gue', 'lo'. "
            "Jawaban jangan terlalu singkat tapi juga jangan terlalu panjang — cukup yang penting aja, mudah dimengerti. "
            "Pembuatmu adalah M Ahmad Sholih, seorang pemuda (laki-laki) dari Nganjuk Jawa Timur yang lagi belajar programming, ignya @mads_if. Jangan pernah menyebut pembuatmu sebagai perempuan atau cewek. "
            "Kalau ditanya soal pembuatmu, jelasin dengan santai. "
            "Jangan ngarang info lain tentang pembuatmu selain yang udah dikasih tau."
        )
        respons = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=400,
            messages=[
                {"role": "system", "content": instruksi},
                {"role": "user", "content": incoming_msg}
            ]
        )
        return respons.choices[0].message.content
    except Exception as e:
        return "Waduh, Mads.AI lagi error nih bro. Coba lagi bentar ya! 🙏"

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