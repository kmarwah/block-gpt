# Block-GPT

This repository contains a Flask web application that generates block diagrams based on user prompts. The application utilizes the GPT-4 model from OpenAI to generate Python code that creates block diagrams using the Graphviz library. Users can interact with the web application to provide prompts and update prompts for generating block diagrams, view the generated diagrams, and download the generated Python code. You can play around with this at: https://block-diagram-generator-rf4gxqg72a-wl.a.run.app/

## Features

- User-friendly web interface to provide prompts and update prompts
- Block diagrams generated using the Graphviz library
- Integration with OpenAI's GPT-4 model for code generation
- Option to download the generated Python code

## Installation

1. Clone the repository:

```
git clone https://github.com/kmarwah/block-gpt.git
cd block-diagram-generator
```

2. Create a virtual environment and activate it:

```
python -m venv venv
source venv/bin/activate  # On Windows, use `venvScriptsactivate`
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Set up Google Cloud Platform (GCP) credentials for accessing the Secret Manager:

- Follow the [GCP documentation](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#creating_secrets) to create a secret for your OpenAI API key
- Update the `secret_project_id`, `secret_name`, and `secret_version` variables in `app.py` with your GCP secret details
- Set up the [Application Default Credentials](https://cloud.google.com/docs/authentication/production#automatically) by exporting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

```
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"  # On Windows, use `set`
```

5. Run the Flask web application:

```
python app.py
```

6. Open your web browser and navigate to http://127.0.0.1:8080 to access the Block Diagram Generator web application.

## Usage

1. Enter your prompt in the "Enter your prompt" input field and click "Generate block diagram" to create a block diagram based on the prompt.
2. To update the block diagram, enter your update prompt in the "Enter your update prompt" input field and click "Generate block diagram" again.
3. To clear the API messages and start over, click the "Clear API Messages" button.
4. To download the generated Python code, click the "Download .py file" button.
