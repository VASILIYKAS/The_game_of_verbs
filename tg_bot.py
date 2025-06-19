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

from google.cloud import dialogflow


def detect_intent_texts(user_id, texts):
    project_id = 'the-game-of-verbs-iefy'
    language_code = 'ru-RU'

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, user_id)

    text_input = dialogflow.TextInput(text=texts, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот с интеграцией Dialogflow. Напиши мне что-нибудь.')


def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_text = update.message.text

    bot_response = detect_intent_texts(user_id, user_text)
    update.message.reply_text(bot_response)


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
        handle_message
        )
    )

    print("ТГ бот успешно запущен!")

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()