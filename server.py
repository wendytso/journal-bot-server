from flask import Flask, request, jsonify
import cohere
import os
import json
import uuid # need? 

app = Flask(__name__)

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


@app.route('/chat', methods=['POST'])

def process_chat():

    co = cohere.Client("WGVT0O8pNsZqNvm4RIhJ78uJ0hdkSsAN3il9ufPd")

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

    return jsonify({'Chatbot Response': chatbot_response}), 200

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=8080)