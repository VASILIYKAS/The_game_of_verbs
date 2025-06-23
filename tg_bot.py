import os

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

from google.cloud import dialogflow


logger = setup_logger('Telegram bot')


def detect_intent_texts(user_id, texts):
    try:
        project_id = os.getenv('PROJECT_ID')
        language_code = 'ru-RU'

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, user_id)

        text_input = dialogflow.TextInput(text=texts, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        return response.query_result.fulfillment_text

    except Exception as e:
        logger.error(
            f"TG bot: "
            f"Dialogflow error: {str(e)} | User: {user_id} | Text: '{texts}'"
        )
        return "Произошла ошибка при обработке запроса"


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот с интеграцией Dialogflow. Напиши мне что-нибудь.')


def handle_message(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        user_text = update.message.text

        bot_response = detect_intent_texts(user_id, user_text)
        update.message.reply_text(bot_response)

    except Exception as e:
        logger.error(
            f"TG bot: "
            f"Message handling failed: {str(e)} | User: {user_id}"
        )
        update.message.reply_text("Произошла ошибка")


def main():
    try:
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
            handle_message
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