from flask import Flask, request, jsonify
from flask_cors import CORS
import cohere
import os
import json
import uuid # need? 

app = Flask(__name__)
CORS(app, origin=os.environ.get('CORS_ORIGIN', '*'))

CHAT_HISTORY_FILE = 'chat_history.json'

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
    co = cohere.Client(os.environ.get('CO_API_KEY'))

    chat_history = load_chat_history()

    user_message = request.get_json().get('user_message',"")
    print(user_message)

    conversation_id = str(uuid.uuid4()) # need? 

    # Define the preamble 
    preamble_override = "You are a therapist. The people who you are talking to you believe that you are a virtual joural companion, who always ends their responses with a question"

    response = co.chat(message=user_message,
                        preamble=preamble_override,
                        stream=True,
                        chat_history=chat_history,
                        return_chat_history=True)
    
    chatbot_response = ""


    for event in response:
        if event.event_type == "text-generation":
            chatbot_response += event.text
    
    print(chatbot_response)

    # Add to chat history
    chat_history.extend(
        [{"role": "USER", "message": user_message},
         {"role": "CHATBOT", "message": chatbot_response}]
    )

    save_chat_history(chat_history)

    print(chat_history)

    return jsonify({'chatbot_response': chatbot_response}), 200

@app.route('/clear', methods=['POST'])

def clear_chat_history():
    try: 
        os.remove(CHAT_HISTORY_FILE)

        load_chat_history()

        return jsonify({'message': 'Chat history cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error clearing chat history: {str(e)}'}), 500

if __name__ == '__main__':
    # run app in debug mode on port 8080
    app.run(debug=True, port=8080)