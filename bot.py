import os

from textwrap import dedent

from dotenv import load_dotenv
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from telegram import Update


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/start')


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main():
    load_dotenv()

    token = os.environ['TG_BOT_TOKEN']
    if not token:
        dedent("""
            Ошибка: Не указан TG_BOT_TOKEN.
            Убедитесь, что он задан в переменных окружения.
        """)

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        echo
        )
    )

    print("Бот успешно запущен!")

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()