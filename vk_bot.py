import os
import random
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
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


def send_message(vk_api, user_id, text):
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 10000)
    )


def handle_message(event, vk_api):
    dialogflow_response = detect_intent_texts(event.user_id, event.text)
    send_message(vk_api, event.user_id, dialogflow_response)


if __name__ == "__main__":
    load_dotenv()

    vk_token = os.environ['VK_TOKEN']
    if not vk_token:
        raise ValueError('Не указан VK_TOKEN в переменных окружения!')

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print("VK бот успешно запущен!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk_api)