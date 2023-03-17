from flask import Flask, request, render_template, session, make_response
from base64 import b64encode
import openai
import os
import graphviz
import tempfile
import logging
from google.cloud import secretmanager
import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()

def get_secret_from_gcp(secret_project_id, secret_name, secret_version):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{secret_project_id}/secrets/{secret_name}/versions/{secret_version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

secret_project_id = "81623212414"

openai.api_key = get_secret_from_gcp(secret_project_id, secret_name="openai_api_key", secret_version="1")

app = Flask(__name__)
app.secret_key = get_secret_from_gcp(secret_project_id, secret_name="flask_app_secret_key", secret_version="1")

def render_and_save_graph(graph):
    graph.render(os.path.join(os.getcwd(), 'block_diagram'), format='png')

def clean_python_code(text):
    comment_start = "'''python"
    comment_end = "'''"
    
    if text.startswith(comment_start) and text.endswith(comment_end):
        # Remove the comment_start, comment_end, and any leading/trailing whitespace
        logging.warning(f"code contained comment: {text}")
        return text[len(comment_start):-len(comment_end)].strip()
    
    comment_start = "```python"
    comment_end = "```"
    
    if text.startswith(comment_start) and text.endswith(comment_end):
        # Remove the comment_start, comment_end, and any leading/trailing whitespace
        logging.warning(f"code contained comment: {text}")
        return text[len(comment_start):-len(comment_end)].strip()
    
    return text

def render_diagram_from_messages(api_messages):
    messages_updated = api_messages
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=api_messages,
        max_tokens=2048
    )

    response_content = response["choices"][0]["message"]["content"]
    cleaned_response_content = clean_python_code(response_content)
    logging.info(f"generated code: {cleaned_response_content}")
    session['generated_code'] = cleaned_response_content
    messages_updated.append({"role": "assistant", "content": cleaned_response_content})
    try:
        exec(cleaned_response_content, {'render_and_save_graph': render_and_save_graph})
    except Exception as e:
        logging.error("Error while rendering graph: %s", e)
    return messages_updated


init_system_prompt = "Your job is to write code which renders a block diagram for the user's prompt. Unless told otherwise, be as thorough and detailed in your response as possible. Your responses should solely consist of python code. Do not include any introduction to the code. The code should use the graphviz python library. Your output should only contain the python code. Create a Graphviz graph object and assign it to the variable named 'graph'. Do not render or save the graph in your code. Instead, call a function called 'render_and_save_graph(graph)' at the end of your code to render and save the graph. The render_and_save_graph function will be passed to the executable, so do not attempt to define it in your code. The rendered block diagram should be saved as a .png file. Do not include any print statements in your code, and do not output the code as a docstring/comment. Every response must be a python program in its entirety. It is imperative that there are no comment blocks in the output. The output must solely consist of a python program which renders the block diagram using graphviz."

@app.route('/', methods=['GET', 'POST'])
def index():
    image_b64 = None

    if request.method == 'POST':
        user_prompt = request.form.get('user_prompt')
        update_prompt = request.form.get('update_prompt')
        action = request.form.get('action')

        if action == 'Clear API Messages':
            session.pop('api_messages', None)
        else:
            if 'api_messages' not in session:
                session['api_messages'] = [
                    {"role": "system", "content": init_system_prompt}
                ]

            if user_prompt:
                logging.info(f"user prompt: {user_prompt}")
                session.pop('api_messages', None)
                session['api_messages'] = [
                    {"role": "system", "content": init_system_prompt}
                ]
                session['api_messages'].append({"role": "assistant", "content": user_prompt})
                session['api_messages'] = render_diagram_from_messages(session['api_messages'])

            if update_prompt:
                logging.info(f"update prompt: {update_prompt}")
                session['api_messages'].append({"role": "assistant", "content": update_prompt})
                session['api_messages'] = render_diagram_from_messages(session['api_messages'])

        if session.get('api_messages'):
            with open("block_diagram.png", "rb") as f:
                image_b64 = b64encode(f.read()).decode("utf-8")

    return render_template('index.html', image_b64=image_b64)

@app.route('/download_code')
def download_code():
    code = session.get('generated_code', '')
    response = make_response(code)
    response.headers.set('Content-Type', 'text/plain')
    response.headers.set('Content-Disposition', 'attachment', filename='generated_code.py')
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)

