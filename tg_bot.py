import os
import functools

from dialogflow_intent import detect_intent_texts
from textwrap import dedent
from logger import setup_logger

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
    update.message.reply_text('Привет! Я бот с интеграцией Dialogflow. Напиши мне что-нибудь.')


def handle_message(update: Update, context: CallbackContext, project_id):
    try:
        user_id = update.message.from_user.id
        user_text = update.message.text

        bot_response = detect_intent_texts(
            project_id=project_id,
            user_id=user_id,
            texts=user_text,
            platform='TG'
        )
        update.message.reply_text(bot_response)

    except Exception:
        logger.exception(
            f"TG bot: "
            f"Message handling failed: {str(e)} | User: {user_id}"
        )
        update.message.reply_text("Произошла ошибка")


def main():
    try:
        load_dotenv()

        logs_dir = os.getenv('LOGS_DIR', 'logs')
        log_file = os.getenv('LOG_FILE', 'bot.log')

        global logger
        logger = setup_logger('Telegram bot', logs_dir, log_file)

        project_id = os.getenv('PROJECT_ID')
        token = os.environ['TG_BOT_TOKEN']
        if not token:
            dedent("""
                Ошибка: Не указан TG_BOT_TOKEN.
                Убедитесь, что он задан в переменных окружения.
            """)

        updater = Updater(token)
        dispatcher = updater.dispatcher

        wrapped_argument = functools.partial(handle_message, project_id=project_id)

        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(MessageHandler(
            Filters.text & ~Filters.command,
            wrapped_argument
            )
        )

        logger.info("Телеграмм бот успешно запущен!")

        updater.start_polling()
        updater.idle()

    except Exception as e:
        logger.critical(e, exc_info=True)
        raise


if __name__ == '__main__':
    main()