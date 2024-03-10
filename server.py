from flask import Flask, request
import cohere
import json
import uuid # need? 

app = Flask(__name__)
co = cohere.Client("WGVT0O8pNsZqNvm4RIhJ78uJ0hdkSsAN3il9ufPd")

@app.route('/chat', methods=['POST'])

def process_chat():

    user_message = request.get_json()

# Create a conversation ID

conversation_id = str(uuid.uuid4())

# Define the preamble
preamble_override = "You are a therapist. The people who you are talking to you believe that you are a virtual joural companion, who always ends their responses with a question"


print('Starting the chat. Type "quit" to end.\n')

while True:
    
    # User message
    message = input("User: ")
    
    # Typing "quit" ends the conversation
    if message.lower() == 'quit':
        print("Ending chat.")
        break
    
    # Chatbot response
    response = co.chat(message=message,
                        preamble=preamble_override,
                        stream=True,
                        conversation_id=conversation_id,
                        return_chat_history=True)
    
    print("Chatbot: ", end='')

    for event in response:
        if event.event_type == "text-generation":
            print(event.text, end='')
    print("\n")