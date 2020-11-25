import os
import logging
from dotenv import load_dotenv
from telegram.ext import Updater
from handlers import *

if not os.getenv('BD2020TOKEN'):
    load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main():  
    _botToken = os.getenv('BD2020TOKEN')
    updater = Updater(token=_botToken, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
