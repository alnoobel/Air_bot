from flask import Flask, request, jsonify, render_template
import openai
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_PcVftGgqGpBCphrijO3lq55m"
user_threads = {}

def call_chatGPT(inString, user_id):
    if user_id in user_threads:
        user_thread_id = user_threads[user_id]
    else:
        thread = client.beta.threads.create()
        user_threads[user_id] = thread.id
        user_thread_id = thread.id

    client.beta.threads.messages.create(
        thread_id=user_thread_id,
        role="user",
        content=inString
    )

    run = client.beta.threads.runs.create(
        assistant_id=ASSISTANT_ID,
        thread_id=user_thread_id
    )

    while run.status != 'completed':
        run = client.beta.threads.runs.retrieve(
            run_id=run.id,
            thread_id=user_thread_id
        )
        time.sleep(1)

    resp = client.beta.threads.messages.list(thread_id=user_thread_id)
    return resp.data[0].content[0].text.value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    response = call_chatGPT(message, user_id)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=9696, debug=True)
