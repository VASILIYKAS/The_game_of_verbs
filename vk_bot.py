import os
import random
import vk_api as vk
from textwrap import dedent
from logger import setup_logger
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
from google.cloud import dialogflow


logger = setup_logger('Telegram bot')


def detect_intent_texts(user_id, texts):
    try:
        project_id = os.getenv('PROJECT_ID')
        language_code = 'ru-RU'

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, user_id)

        text_input = dialogflow.TextInput(
            text=texts, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        if response.query_result.intent.is_fallback:
            return None

        return response.query_result.fulfillment_text

    except Exception as e:
        logger.error(
            f"VK bot: "
            f"Dialogflow error: {str(e)} | User: {user_id} | Text: '{text}'"
        )
        return "Произошла ошибка при обработке запроса"


def send_message(vk_api, user_id, text):
    try:
        vk_api.messages.send(
            user_id=user_id,
            message=text,
            random_id=random.randint(1, 10000)
        )

    except Exception as e:
        logger.error(
            f"В VK боте произошла ошибка при отправке сообщения: {str(e)} | User: {user_id} | Text: '{text}'")


def handle_message(event, vk_api):
    try:
        dialogflow_response = detect_intent_texts(event.user_id, event.text)
        if dialogflow_response is not None:
            send_message(vk_api, event.user_id, dialogflow_response)

    except Exception as e:
        logger.error(
            f"VK bot: "
            f"Message handling failed: {str(e)}"
        )


def main():
    try:
        load_dotenv()

        vk_token = os.environ['VK_TOKEN']
        if not vk_token:
            dedent("""
                Ошибка: Не указан VK_TOKEN.
                Убедитесь, что он задан в переменных окружения.
            """)

        vk_session = vk.VkApi(token=vk_token)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)

        logger.info("VK бот успешно запущен!")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                handle_message(event, vk_api)

    except Exception as e:
        logger.critical(e, exc_info=True)
        raise


if __name__ == '__main__':
    main()
