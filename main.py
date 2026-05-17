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
            "Kirim pesan apapun dan saya akan membalasnya menggunakan AI