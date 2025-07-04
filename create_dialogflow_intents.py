import json
import os
from dotenv import load_dotenv
from google.cloud import dialogflow


def create_intent(project_id):

    with open('questions.json', 'r', encoding='utf-8') as json_file:
        question_json = json.load(json_file)

    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    created_intents = []

    for intent_name, intent_data in question_json.items():
        training_phrases = []

        for phrase in intent_data['questions']:
            part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
            training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)

        message_texts = [intent_data["answer"]]
        text = dialogflow.Intent.Message.Text(text=message_texts)
        message = dialogflow.Intent.Message(text=text)

        intent = dialogflow.Intent(
            display_name=intent_name,
            training_phrases=training_phrases,
            messages=[message]
        )

        response = intents_client.create_intent(
            request={'parent': parent, 'intent': intent, 'language_code': 'ru'}
        )
        created_intents.append(intent_name)

        return created_intents


if __name__ == "__main__":
    load_dotenv()

    project_id = os.getenv('PROJECT_ID')

    intents = create_intent(project_id)
    for intent in intents:
        print(f'Интент "{intent}" успешно создан!')
