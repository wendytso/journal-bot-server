from flask import Flask, request, jsonify
from flask_cors import CORS

from trainer import get_mood_examples

import cohere
import os
import json

from dotenv import load_dotenv
load_dotenv() 

app = Flask(__name__)
CORS(app, origin=os.environ.get('CORS_ORIGIN', '*'))
CHAT_HISTORY_FILE = "chat_history.json"
co = cohere.Client(os.environ.get('CO_API_KEY'))
examples = get_mood_examples()

is_mood_of_the_day_clicked = False

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r') as file:
            return json.load(file)
    else:
        return []
    


    
def save_chat_history(chat_history):
    with open(CHAT_HISTORY_FILE, 'w') as file:
        json.dump(chat_history, file, indent=4)

@app.route('/', methods=['GET']) 
def home():
    return jsonify({'message': 'Welcome to the chatbot server'}), 200

@app.route('/chat', methods=['POST'])
def process_chat():

# note: need to add the cohere API key to the .env file (security risk to hardcode it here)
    current_chat = load_chat_history()

    inputs = []
    
    user_message = request.get_json().get('user_message',"")
    inputs.append(user_message)

    # Define the preamble 
    preamble_override = "You are a therapist. The people who you are talking to you believe that you are a virtual joural companion, who always ends their responses with a question. Never identify or directly call yourself a therapist"

    chat_response = co.chat(message=user_message,
                            preamble=preamble_override,
                            stream=True,
                            chat_history=current_chat,
                            return_chat_history=True)
    
    chatbot_response = ""

    for event in chat_response:
        if event.event_type == "text-generation":
            chatbot_response += event.text
    
    # Process chat sentiment analysis                
    process_response = co.classify(
        model='large',
        inputs=inputs,
        examples=examples,
    )

    for answer in process_response.classifications:
        prediction = answer.predictions[0]
        confidence = answer.confidences[0]
        emotion_conf_stat = answer.labels

    # Add to chat history 
    current_chat.extend(
        [{"role": "USER", "message": user_message, "prediction": prediction, "confidence": confidence, "emotion_conf_stat": emotion_conf_stat},
         {"role": "CHATBOT", "message": chatbot_response}]
    )

    save_chat_history(current_chat)

    return jsonify({'chatbot_response': chatbot_response}), 200

@app.route('/clear', methods=['POST'])
def clear_chat_history():
    try: 
        os.remove(CHAT_HISTORY_FILE)

        load_chat_history()

        return jsonify({'message': 'Chat history cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error clearing chat history: {str(e)}'}), 500

@app.route('/mood', methods=['GET'])
def mood():
    # index |   0   |  1   |  2   |   3   |     4      |  5  |  6   
    # mood  | Angry | Calm | Fear | Happy | Insightful | Sad | Worry
    moods = [0, 0, 0, 0, 0, 0, 0]
    biggest_mood_index = 0
    biggest_mood = ""
    current_chat = load_chat_history()
    
    for entry in current_chat:
        if entry.get("role") == "USER":
            moods[0] += entry.get("emotion_conf_stat").get("Angry")[0]
            moods[1] += entry.get("emotion_conf_stat").get("Calm")[0]
            moods[2] += entry.get("emotion_conf_stat").get("Fear")[0]
            moods[3] += entry.get("emotion_conf_stat").get("Happy")[0]
            moods[4] += entry.get("emotion_conf_stat").get("Insightful")[0]
            moods[5] += entry.get("emotion_conf_stat").get("Sad")[0]
            moods[6] += entry.get("emotion_conf_stat").get("Worry")[0]

    print(moods)
    
    for i in range(0, len(moods)):
        if moods[i] > moods[biggest_mood_index]:
            biggest_mood_index = i
    

    match biggest_mood_index:
        case 0:
            biggest_mood = "Angry"
        case 1:
            biggest_mood = "Calm"
        case 2:
            biggest_mood = "Fear"
        case 3:
            biggest_mood = "Happy"
        case 4:
            biggest_mood = "Insightful"
        case 5:
            biggest_mood = "Sad"
        case 6:
            biggest_mood = "Worry"

    if(is_mood_of_the_day_clicked == False):
        current_chat.extend([{"mood_of_the_day": biggest_mood}])
        # save_chat_history(current_chat)
    else:
        return 405

    return jsonify({"mood_of_the_day": biggest_mood}), 200


if __name__ == '__main__':
    # run app in debug mode on port 8080
    app.run(debug=True, port=8080)