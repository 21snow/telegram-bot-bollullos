import os
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask, request
from PIL import Image, ImageFilter, PngImagePlugin

# Crear una aplicación Flask
app = Flask(__name__)

# Función para manejar webhooks de Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK"

# Función para modificar PNG y cambiar/eliminar metadatos
def modificar_png(ruta_imagen, nueva_ruta):
    imagen = Image.open(ruta_imagen)

    # Ajustar ligeramente las dimensiones (ejemplo: reducir en un 5%)
    nuevo_tamaño = (int(imagen.size[0] * 0.95), int(imagen.size[1] * 0.95))
    imagen = imagen.resize(nuevo_tamaño)

    # Aplicar un filtro (por ejemplo, suavizar)
    imagen = imagen.filter(ImageFilter.SMOOTH)

    # Modificar los metadatos (propiedades de la imagen)
    info = PngImagePlugin.PngInfo()
    info.add_text("Author", "Modificado por el bot")
    info.add_text("Description", "Imagen redimensionada y suavizada")

    # Guardar la imagen modificada con los nuevos metadatos
    imagen.save(nueva_ruta, format="PNG", pnginfo=info)
    return nueva_ruta

# Función para manejar imágenes recibidas
def handle_image(update: Update, context: CallbackContext) -> None:
    file = update.message.photo[-1].get_file()
    file_path = file.download()

    # Rutas para guardar las imágenes modificadas
    nueva_ruta_png = "/tmp/modificado.png"  # Debes guardar en /tmp en Cloud Functions

    if file_path.endswith('.png'):
        nueva_ruta = modificar_png(file_path, nueva_ruta_png)
    else:
        update.message.reply_text("Formato no soportado. Solo se admiten PNG.")
        return

    # Enviar de vuelta la imagen modificada
    update.message.reply_document(document=open(nueva_ruta, 'rb'))

# Inicializar el bot y configurar los manejadores
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Manejadores del bot
dispatcher.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text('¡Hola! Envía una imagen PNG y la modificaré.')))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))
