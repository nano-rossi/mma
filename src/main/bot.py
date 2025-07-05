from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Token del bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# URL de tu API local
API_URL = "http://localhost:8000/query"

# Función que se ejecuta cuando el bot recibe un mensaje
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    # Enviamos el mensaje a la API local
    try:
        response = requests.post(API_URL, json={"chat_id": user_id, "query": text})
        print(f"Enviado a API. Status: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar a API: {e}")

    # Podés responderle algo al usuario si querés
    await update.message.reply_text("Estamos procesando tu consulta.")

# Configurar y correr el bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot corriendo...")
    app.run_polling()

if __name__ == '__main__':
    main()
