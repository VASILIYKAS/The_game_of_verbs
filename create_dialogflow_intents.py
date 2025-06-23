import json
import os
from google.cloud import dialogflow


def create_intent():
    project_id = os.getenv('PROJECT_ID')
    with open('questions.json', 'r', encoding='utf-8') as my_file:
        question_json = json.load(my_file)

    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

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
        print(f'Интент "{intent_name}" успешно создан!')


if __name__ == "__main__":
    create_intent()