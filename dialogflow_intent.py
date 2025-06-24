import logging
from google.cloud import dialogflow


logger = logging.getLogger('Dialogflow')


def detect_intent_texts(project_id, user_id, texts, language_code='ru-RU', platform='unknown'):
    try:
        session_user_id = f"{platform}_{user_id}"
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_user_id)

        text_input = dialogflow.TextInput(text=texts, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        if hasattr(response.query_result.intent, 'is_fallback') and response.query_result.intent.is_fallback:
            return None

        return response.query_result.fulfillment_text

    except Exception:
        logger.exception(
            f"{platform} bot: Dialogflow error: User: {user_id} | Text: '{texts}'"
        )
        return "Произошла ошибка при обработке запроса"