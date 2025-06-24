import os
import random
import vk_api as vk
from textwrap import dedent
from logger import setup_logger
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
from dialogflow_intent import detect_intent_texts


def send_message(vk_api, user_id, text):
    try:
        vk_api.messages.send(
            user_id=user_id,
            message=text,
            random_id=random.randint(1, 10000)
        )

    except Exception:
        logger.exception(
            f"В VK боте произошла ошибка при отправке сообщения: {str(e)} | User: {user_id} | Text: '{text}'"
        )


def handle_message(event, vk_api, project_id):
    try:
        dialogflow_response = detect_intent_texts(
            project_id=project_id,
            user_id=event.user_id,
            texts=event.text,
            platform='VK'
        )

        if dialogflow_response is not None:
            send_message(vk_api, event.user_id, dialogflow_response)

    except Exception:
        logger.exception(
            f"VK bot: "
            f"Message handling failed: {str(e)}"
        )


def main():
    try:
        load_dotenv()

        logs_dir = os.getenv('LOGS_DIR', 'logs')
        log_file = os.getenv('LOG_FILE', 'bot.log')

        global logger
        logger = setup_logger('VK bot', logs_dir, log_file)

        project_id = os.getenv('PROJECT_ID')
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
                handle_message(event, vk_api, project_id)

    except Exception as e:
        logger.critical(e, exc_info=True)
        raise


if __name__ == '__main__':
    main()
